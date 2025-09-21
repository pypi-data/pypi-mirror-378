import os
from traceback import print_exc

from rlbot import flat
from rlbot.interface import (
    RLBOT_SERVER_IP,
    RLBOT_SERVER_PORT,
    MsgHandlingResult,
    SocketRelay,
)
from rlbot.managers.rendering import Renderer
from rlbot.utils import fill_desired_game_state
from rlbot.utils.logging import DEFAULT_LOGGER, get_logger


class Bot:
    """
    A convenience base class for regular bots.
    The base class handles the setup and communication with the rlbot server.
    Inherit from this class and override `get_output` to make a basic bot.
    Initialization that require `index`, `name`, `team`, or game data must be done
    in `initialize` as their values are not ready in the constructor.
    """

    logger = DEFAULT_LOGGER

    team: int = -1
    index: int = -1
    name: str = ""
    player_id: int = 0

    match_config = flat.MatchConfiguration()
    """
    Contains info about what map you're on, game mode, mutators, etc.
    """

    field_info = flat.FieldInfo()
    """
    Contains info about the map, such as the locations of boost pads and goals.
    """

    ball_prediction = flat.BallPrediction()
    """
    A simulated prediction of the ball's trajectory including collisions with field geometry (but not cars).
    """

    _initialized_bot = False
    _has_match_settings = False
    _has_field_info = False
    _has_player_mapping = False

    _latest_packet: flat.GamePacket | None = None
    _latest_prediction = flat.BallPrediction()

    def __init__(self, default_agent_id: str | None = None):
        agent_id = os.environ.get("RLBOT_AGENT_ID") or default_agent_id

        if agent_id is None:
            self.logger.critical(
                "Environment variable RLBOT_AGENT_ID is not set and no default agent id is passed to "
                "the constructor of the bot. If you are starting your bot manually, please set it "
                "manually, e.g. `RLBOT_AGENT_ID=<agent_id> python yourbot.py`"
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
        self._game_interface.controllable_team_info_handlers.append(
            self._handle_controllable_team_info
        )
        self._game_interface.packet_handlers.append(self._handle_packet)
        self._game_interface.rendering_status_handlers.append(
            self.rendering_status_update
        )

        self.renderer = Renderer(self._game_interface)

    def _try_initialize(self):
        if (
            self._initialized_bot
            or not self._has_match_settings
            or not self._has_field_info
            or not self._has_player_mapping
        ):
            # Not ready to initialize
            return

        for player in self.match_config.player_configurations:
            match player.variety:
                case flat.CustomBot(name):
                    if player.player_id == self.player_id:
                        self.name = name
                        self.logger = get_logger(self.name)
                        break
        else:  # else block runs if break was not hit
            self.logger.warning(
                "Bot with agent id '%s' did not find itself in the match configuration",
                self._game_interface.agent_id,
            )

        try:
            self.initialize()
        except Exception as e:
            self.logger.critical(
                "Bot %s failed to initialize due the following error: %s", self.name, e
            )
            print_exc()
            exit()

        self._initialized_bot = True
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

    def _handle_controllable_team_info(
        self, player_mappings: flat.ControllableTeamInfo
    ):
        self.team = player_mappings.team
        controllable = player_mappings.controllables[0]
        self.player_id = controllable.identifier
        self.index = controllable.index
        self._has_player_mapping = True

        self._try_initialize()

    def _handle_ball_prediction(self, ball_prediction: flat.BallPrediction):
        self._latest_prediction = ball_prediction

    def _handle_packet(self, packet: flat.GamePacket):
        self._latest_packet = packet

    def _packet_processor(self, packet: flat.GamePacket):
        if len(packet.players) <= self.index:
            return

        self.ball_prediction = self._latest_prediction

        try:
            controller = self.get_output(packet)
        except Exception as e:
            self.logger.error(
                "Bot %s encountered an error while processing game packet: %s",
                self.name,
                e,
            )
            print_exc()
            if self.renderer.is_rendering():
                self.renderer.end_rendering()
            return

        player_input = flat.PlayerInput(self.index, controller)
        self._game_interface.send_msg(player_input)

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
        Runs the bot. This operation is blocking until the match ends.
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
        except Exception as e:
            self.logger.error("Unexpected error: %s", e)
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
        if update.is_bot and update.index == self.index:
            self.renderer.can_render = update.status

    def update_rendering_status(
        self,
        status: bool,
        index: int | None = None,
        is_bot: bool = True,
    ):
        """
        Requests the server to update the status of the ability for this bot to render.
        Will be ignored if rendering has been set to AlwaysOff in the match configuration.
        If the status is successfully updated, the `self.rendering_status_update` method will be called which will update `self.renderer.can_render`.

        - `status`: `True` to enable rendering, `False` to disable.
        - `index`: The index of the bot to update. If `None`, uses the bot's own index.
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
        - `team_only`: If True, only your team will receive the message.
        """
        self._game_interface.send_msg(
            flat.MatchComm(
                self.index,
                self.team,
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

    def set_loadout(self, loadout: flat.PlayerLoadout, index: int | None = None):
        """
        Sets the loadout of a bot.
        Can be used to select or generate a loadout for the match when called inside `initialize`.
        Does nothing if called outside `initialize` unless state setting is enabled in which case it
        respawns the car with the new loadout.
        """
        self._game_interface.send_msg(flat.SetLoadout(index or self.index, loadout))

    def initialize(self):
        """
        Called when the bot is ready for initialization. Field info, match configuration, name, index, and team are
        fully loaded at this point, and will not return garbage data unlike in `__init__`.
        """

    def retire(self):
        """Called when the bot is shut down"""

    def get_output(self, packet: flat.GamePacket) -> flat.ControllerState:
        """
        This method is where the main logic of the bot goes.
        The input is the latest game packet and the controller state for the next tick must be returned.
        """
        raise NotImplementedError
