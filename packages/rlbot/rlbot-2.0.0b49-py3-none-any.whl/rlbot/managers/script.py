import os
from traceback import print_exc

from rlbot import flat
from rlbot.interface import (
    RLBOT_SERVER_IP,
    RLBOT_SERVER_PORT,
    MsgHandlingResult,
    SocketRelay,
)
from rlbot.managers import Renderer
from rlbot.utils import fill_desired_game_state
from rlbot.utils.logging import DEFAULT_LOGGER, get_logger


class Script:
    """
    A convenience base class for scripts that handles the setup and communication with the rlbot server.
    Inherit from this class and override `handle_packet` to make a basic script.
    Initialization that require `index`, `name`, or game data must be done in `initialize` as their values
    are not ready in the constructor.
    """

    logger = DEFAULT_LOGGER

    index: int = 0
    name: str = "UnknownScript"

    match_config = flat.MatchConfiguration()
    field_info = flat.FieldInfo()
    ball_prediction = flat.BallPrediction()

    _initialized_script = False
    _has_match_settings = False
    _has_field_info = False

    _latest_packet: flat.GamePacket | None = None
    _latest_prediction = flat.BallPrediction()

    def __init__(self, default_agent_id: str | None = None):
        agent_id = os.environ.get("RLBOT_AGENT_ID") or default_agent_id

        if agent_id is None:
            self.logger.critical(
                "Environment variable RLBOT_AGENT_ID is not set and no default agent id is passed to "
                "the constructor of the script. If you are starting your script manually, please set "
                "it manually, e.g. `RLBOT_AGENT_ID=<agent_id> python yourscript.py`"
            )
            exit(1)

        self._game_interface = SocketRelay(agent_id, logger=self.logger)
        self._game_interface.match_config_handlers.append(self._handle_match_config)
        self._game_interface.field_info_handlers.append(self._handle_field_info)
        self._game_interface.match_comm_handlers.append(
            self._handle_match_communication
        )
        self._game_interface.ball_prediction_handlers.append(
            self._handle_ball_prediction
        )
        self._game_interface.packet_handlers.append(self._handle_packet)
        self._game_interface.rendering_status_handlers.append(
            self.rendering_status_update
        )

        self.renderer = Renderer(self._game_interface)

    def _try_initialize(self):
        if (
            self._initialized_script
            or not self._has_match_settings
            or not self._has_field_info
        ):
            return

        self.logger = get_logger(self.name)

        for i, script in enumerate(self.match_config.script_configurations):
            if script.agent_id == self._game_interface.agent_id:
                self.index = i
                self.name = script.name
                break
        else:  # else block runs if break was not hit
            self.logger.warning(
                "Script with agent id '%s' did not find itself in the match configuration",
                self._game_interface.agent_id,
            )

        try:
            self.initialize()
        except Exception as e:
            self.logger.critical(
                "Script %s failed to initialize due the following error: %s",
                self.name,
                e,
            )
            print_exc()
            exit()

        self._initialized_script = True
        self._game_interface.send_msg(flat.InitComplete())

    def _handle_match_config(self, match_config: flat.MatchConfiguration):
        self.match_config = match_config
        self._has_match_settings = True
        self.can_render = (
            match_config.enable_rendering == flat.DebugRendering.OnByDefault
        )

        self._try_initialize()

    def _handle_field_info(self, field_info: flat.FieldInfo):
        self.field_info = field_info
        self._has_field_info = True
        self._try_initialize()

    def _handle_ball_prediction(self, ball_prediction: flat.BallPrediction):
        self._latest_prediction = ball_prediction

    def _handle_packet(self, packet: flat.GamePacket):
        self._latest_packet = packet

    def _packet_processor(self, packet: flat.GamePacket):
        self.ball_prediction = self._latest_prediction

        try:
            self.handle_packet(packet)
        except Exception as e:
            self.logger.error(
                "Script %s encountered an error to RLBot: %s", self.name, e
            )
            if self.renderer.is_rendering():
                self.renderer.end_rendering()
            print_exc()

    def _run(self):
        running = True

        while running:
            # If there might be more messages,
            # check for another one with blocking=False
            # if there are no more messages, process the latest packet
            # then wait for the next message with blocking=True
            match self._game_interface.handle_incoming_messages(
                blocking=self._latest_packet is None
            ):
                case MsgHandlingResult.TERMINATED:
                    running = False
                case MsgHandlingResult.NO_INCOMING_MSGS:
                    if self._latest_packet is not None:
                        self._packet_processor(self._latest_packet)
                        self._latest_packet = None
                case _:
                    pass

    def run(
        self,
        *,
        wants_match_communications: bool = True,
        wants_ball_predictions: bool = True,
    ):
        """
        Runs the script. This operation is blocking until the match ends.
        """

        rlbot_server_ip = os.environ.get("RLBOT_SERVER_IP", RLBOT_SERVER_IP)
        rlbot_server_port = int(os.environ.get("RLBOT_SERVER_PORT", RLBOT_SERVER_PORT))

        try:
            self._game_interface.connect(
                wants_match_communications=wants_match_communications,
                wants_ball_predictions=wants_ball_predictions,
                rlbot_server_ip=rlbot_server_ip,
                rlbot_server_port=rlbot_server_port,
            )

            self._run()
        finally:
            self.retire()
            del self._game_interface

    def _handle_match_communication(self, match_comm: flat.MatchComm):
        self.handle_match_comm(
            match_comm.index,
            match_comm.team,
            match_comm.content,
            match_comm.display,
            match_comm.team_only,
        )

    def rendering_status_update(self, update: flat.RenderingStatus):
        """
        Called when the server sends a rendering status update for ANY bot or script.

        By default, this will update `self.renderer.can_render` if appropriate.
        """
        if not update.is_bot and update.index == self.index:
            self.renderer.can_render = update.status

    def update_rendering_status(
        self,
        status: bool,
        index: int | None = None,
        is_bot: bool = False,
    ):
        """
        Requests the server to update the status of the ability for this bot to render.
        Will be ignored if rendering has been set to AlwaysOff in the match configuration.
        If the status is successfully updated, the `self.rendering_status_update` method will be called which will update `self.renderer.can_render`.

        - `status`: `True` to enable rendering, `False` to disable.
        - `index`: The index of the bot to update. If `None`, uses the script's own index.
        - `is_bot`: `True` if `index` is a bot index, `False` if it is a script index.
        """
        self._game_interface.send_msg(
            flat.RenderingStatus(self.index if index is None else index, is_bot, status)
        )

    def handle_match_comm(
        self,
        index: int,
        team: int,
        content: bytes,
        display: str | None,
        team_only: bool,
    ):
        """
        Called when a match communication message is received.
        See `send_match_comm`.
        NOTE: Messages from scripts will have `team == 2` and the index will be its index in the match configuration.
        """

    def send_match_comm(
        self, content: bytes, display: str | None = None, team_only: bool = False
    ):
        """
        Emits a match communication message to other bots and scripts.

        - `content`: The content of the message containing arbitrary data.
        - `display`: The message to be displayed in the game in "quick chat", or `None` to display nothing.
        - `team_only`: If True, only your team will receive the message. For scripts, this means other scripts.
        """
        self._game_interface.send_msg(
            flat.MatchComm(
                self.index,
                2,
                team_only,
                display,
                content,
            )
        )

    def set_game_state(
        self,
        balls: dict[int, flat.DesiredBallState] = {},
        cars: dict[int, flat.DesiredCarState] = {},
        match_info: flat.DesiredMatchInfo | None = None,
        commands: list[str] = [],
    ):
        """
        Sets the game to the desired state.
        Through this it is possible to manipulate the position, velocity, and rotations of cars and balls, and more.
        See wiki for a full break down and examples.
        """

        game_state = fill_desired_game_state(balls, cars, match_info, commands)
        self._game_interface.send_msg(game_state)

    def set_loadout(self, loadout: flat.PlayerLoadout, index: int):
        """
        Sets the loadout of a bot.

        Will be ignored if called when state setting is disabled.
        """
        self._game_interface.send_msg(flat.SetLoadout(index, loadout))

    def initialize(self):
        """
        Called when the script is ready for initialization. Field info, match configuration, name, and index are
        fully loaded at this point, and will not return garbage data unlike in `__init__`.
        """

    def retire(self):
        """Called when the script is shut down"""

    def handle_packet(self, packet: flat.GamePacket) -> None:
        """
        This method is where the main logic of the bot goes.
        The input is the latest game packet.
        """
        raise NotImplementedError
