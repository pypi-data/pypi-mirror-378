import tomllib
from pathlib import Path
from typing import Any, Literal

import rlbot.flat as flat
from rlbot.utils.os_detector import CURRENT_OS, OS


class ConfigParsingException(Exception):
    pass


def __enum(table: dict[str, str | Any], key: str, enum: Any, default: int = 0) -> Any:
    if key not in table:
        return enum(default)
    try:
        for i in range(100000):
            if str(enum(i)).split(".")[-1].lower() == table[key].lower():
                return enum(i)
    except ValueError:
        raise ConfigParsingException(
            f"Invalid value {repr(table[key])} for key '{key}'."
        )


def __str(table: dict[str, str | Any], key: str, default: str = "") -> str:
    v = table.get(key, default)
    if isinstance(v, str):
        return v
    raise ConfigParsingException(f"'{key}' has value {repr(v)}. Expected a string.")


def __bool(table: dict[str, bool | Any], key: str, default: bool = False) -> bool:
    v = table.get(key, default)
    if isinstance(v, bool):
        return v
    raise ConfigParsingException(f"'{key}' has value {repr(v)}. Expected a bool.")


def __int(table: dict[str, int | Any], key: str, default: int = 0) -> int:
    v = table.get(key, default)
    if isinstance(v, int):
        return v
    raise ConfigParsingException(f"'{key}' has value {repr(v)}. Expected an int.")


def __table(table: dict[str, dict[str, Any] | Any], key: str) -> dict[str, Any]:
    v = table.get(key, dict())
    if isinstance(v, dict):
        return v  # type: ignore
    raise ConfigParsingException(f"'{key}' has value {repr(v)}. Expected a table.")


def __team(table: dict[str, Literal["blue", "orange", 0, 1] | Any]) -> int:
    if "team" not in table:
        return 0
    v = table["team"]
    if isinstance(v, str):
        if v.lower() == "blue":
            return 0
        if v.lower() == "orange":
            return 1
    if isinstance(v, int):
        if 0 <= v <= 1:
            return v
    raise ConfigParsingException(
        f'\'team\' has value {repr(v)}. Expected a 0, 1, "blue", or "orange".'
    )


def load_match_config(config_path: Path | str) -> flat.MatchConfiguration:
    """
    Reads the match toml file at the provided path and creates the corresponding MatchConfiguration.
    """
    config_path = Path(config_path)
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    rlbot_table = __table(config, "rlbot")
    match_table = __table(config, "match")
    mutator_table = __table(config, "mutators")

    players: list[flat.PlayerConfiguration] = []
    for car_table in config.get("cars", []):
        car_config = __str(car_table, "config_file")
        name = __str(car_table, "name")
        team = __team(car_table)
        loadout_file = __str(car_table, "loadout_file") or None
        skill = __enum(
            car_table, "skill", flat.PsyonixSkill, int(flat.PsyonixSkill.AllStar)
        )
        variant = __str(car_table, "type", "rlbot").lower()

        match variant:
            case "rlbot":
                abs_config_path = (config_path.parent / car_config).resolve()
                players.append(
                    load_player_config(abs_config_path, team, name, loadout_file)
                )
            case "psyonix":
                abs_config_path = (
                    (config_path.parent / car_config).resolve() if car_config else None
                )
                players.append(
                    load_psyonix_config(
                        team,
                        skill,
                        name,
                        loadout_file,
                        abs_config_path,
                    )
                )
            case "human":
                players.append(get_human(team))
            case t:
                raise ConfigParsingException(
                    f"Invalid player type {repr(t)} for player {len(players)}."
                )

    scripts: list[flat.ScriptConfiguration] = []
    for script_table in config.get("scripts", []):
        if script_config := __str(script_table, "config_file"):
            abs_config_path = (config_path.parent / script_config).resolve()
            scripts.append(load_script_config(abs_config_path))
        else:
            scripts.append(flat.ScriptConfiguration())

    mutators = flat.MutatorSettings(
        match_length=__enum(mutator_table, "match_length", flat.MatchLengthMutator),
        max_score=__enum(mutator_table, "max_score", flat.MaxScoreMutator),
        multi_ball=__enum(mutator_table, "multi_ball", flat.MultiBallMutator),
        overtime=__enum(mutator_table, "overtime", flat.OvertimeMutator),
        series_length=__enum(mutator_table, "series_length", flat.SeriesLengthMutator),
        game_speed=__enum(mutator_table, "game_speed", flat.GameSpeedMutator),
        ball_max_speed=__enum(
            mutator_table, "ball_max_speed", flat.BallMaxSpeedMutator
        ),
        ball_type=__enum(mutator_table, "ball_type", flat.BallTypeMutator),
        ball_weight=__enum(mutator_table, "ball_weight", flat.BallWeightMutator),
        ball_size=__enum(mutator_table, "ball_size", flat.BallSizeMutator),
        ball_bounciness=__enum(
            mutator_table, "ball_bounciness", flat.BallBouncinessMutator
        ),
        boost_amount=__enum(mutator_table, "boost_amount", flat.BoostAmountMutator),
        rumble=__enum(mutator_table, "rumble", flat.RumbleMutator),
        boost_strength=__enum(
            mutator_table, "boost_strength", flat.BoostStrengthMutator
        ),
        gravity=__enum(mutator_table, "gravity", flat.GravityMutator),
        demolish=__enum(mutator_table, "demolish", flat.DemolishMutator),
        respawn_time=__enum(mutator_table, "respawn_time", flat.RespawnTimeMutator),
        max_time=__enum(mutator_table, "max_time", flat.MaxTimeMutator),
        game_event=__enum(mutator_table, "game_event", flat.GameEventMutator),
        audio=__enum(mutator_table, "audio", flat.AudioMutator),
    )

    try:
        enable_rendering = (
            flat.DebugRendering.OnByDefault
            if __bool(match_table, "enable_rendering")
            else flat.DebugRendering.OffByDefault
        )
    except ConfigParsingException:
        enable_rendering = __enum(
            match_table, "enable_rendering", flat.DebugRendering.AlwaysOff
        )

    return flat.MatchConfiguration(
        launcher=__enum(rlbot_table, "launcher", flat.Launcher),
        launcher_arg=__str(rlbot_table, "launcher_arg"),
        auto_start_agents=__bool(rlbot_table, "auto_start_agents", True),
        wait_for_agents=__bool(rlbot_table, "wait_for_agents", True),
        game_map_upk=__str(match_table, "game_map_upk"),
        player_configurations=players,
        script_configurations=scripts,
        game_mode=__enum(match_table, "game_mode", flat.GameMode),
        skip_replays=__bool(match_table, "skip_replays"),
        instant_start=__bool(match_table, "instant_start"),
        mutators=mutators,
        existing_match_behavior=__enum(
            match_table, "existing_match_behavior", flat.ExistingMatchBehavior
        ),
        enable_rendering=enable_rendering,
        enable_state_setting=__bool(match_table, "enable_state_setting"),
        freeplay=__bool(match_table, "freeplay"),
    )


def load_player_loadout(path: Path | str, team: int) -> flat.PlayerLoadout:
    """
    Reads the loadout toml file at the provided path and extracts the `PlayerLoadout` for the given team.
    """
    with open(path, "rb") as f:
        config = tomllib.load(f)

    table_name = "blue_loadout" if team == 0 else "orange_loadout"
    loadout = __table(config, table_name)
    paint = None
    if paint_table := __table(loadout, "paint"):
        paint = flat.LoadoutPaint(
            car_paint_id=__int(paint_table, "car_paint_id"),
            decal_paint_id=__int(paint_table, "decal_paint_id"),
            wheels_paint_id=__int(paint_table, "wheels_paint_id"),
            boost_paint_id=__int(paint_table, "boost_paint_id"),
            antenna_paint_id=__int(paint_table, "antenna_paint_id"),
            hat_paint_id=__int(paint_table, "hat_paint_id"),
            trails_paint_id=__int(paint_table, "trails_paint_id"),
            goal_explosion_paint_id=__int(paint_table, "goal_explosion_paint_id"),
        )

    return flat.PlayerLoadout(
        team_color_id=__int(loadout, "team_color_id"),
        custom_color_id=__int(loadout, "custom_color_id"),
        car_id=__int(loadout, "car_id"),
        decal_id=__int(loadout, "decal_id"),
        wheels_id=__int(loadout, "wheels_id"),
        boost_id=__int(loadout, "boost_id"),
        antenna_id=__int(loadout, "antenna_id"),
        hat_id=__int(loadout, "hat_id"),
        paint_finish_id=__int(loadout, "paint_finish_id"),
        custom_finish_id=__int(loadout, "custom_finish_id"),
        engine_audio_id=__int(loadout, "engine_audio_id"),
        trails_id=__int(loadout, "trails_id"),
        goal_explosion_id=__int(loadout, "goal_explosion_id"),
        loadout_paint=paint,
    )


def load_player_config(
    path: Path | str,
    team: int,
    name_override: str | None = None,
    loadout_override: Path | str | None = None,
) -> flat.PlayerConfiguration:
    """
    Reads the bot toml file at the provided path and
    creates a `PlayerConfiguration` of the given type for the given team.
    """
    path = Path(path)
    with open(path, "rb") as f:
        config = tomllib.load(f)

    settings = __table(config, "settings")

    root_dir = path.parent.absolute()
    if "root_dir" in settings:
        root_dir /= Path(__str(settings, "root_dir"))

    run_command = __str(settings, "run_command")
    if CURRENT_OS == OS.LINUX and "run_command_linux" in settings:
        run_command = __str(settings, "run_command_linux")

    loadout_path = (
        path.parent / Path(__str(settings, "loadout_file"))
        if "loadout_file" in settings
        else None
    )
    loadout_path = loadout_override or loadout_path
    loadout = (
        load_player_loadout(loadout_path, team) if loadout_path is not None else None
    )

    return flat.PlayerConfiguration(
        flat.CustomBot(
            name_override or __str(settings, "name"),
            str(root_dir),
            run_command,
            loadout,
            __str(settings, "agent_id"),
            __bool(settings, "hivemind"),
        ),
        team,
        0,
    )


def load_psyonix_config(
    team: int,
    skill_level: flat.PsyonixSkill,
    name_override: str | None = None,
    loadout_override: Path | str | None = None,
    path: Path | str | None = None,
) -> flat.PlayerConfiguration:
    """
    Creates a `PlayerConfiguration` for a Psyonix bot of the given team and skill.
    If a path is provided, it will be used override the default name and loadout.
    """
    name = name_override
    loadout_path = loadout_override

    # Don't parse the toml file if we have no data we need to extract,
    # even if a path to a toml file is provided.
    if path is not None and (name is None or loadout_path is None):
        path = Path(path)
        with open(path, "rb") as f:
            config = tomllib.load(f)

            settings = __table(config, "settings")

            if name is None:
                name = __str(settings, "name")

            if loadout_path is None:
                loadout_path = (
                    path.parent / Path(__str(settings, "loadout_file"))
                    if "loadout_file" in settings
                    else None
                )

    loadout = (
        load_player_loadout(loadout_path, team) if loadout_path is not None else None
    )

    return flat.PlayerConfiguration(
        flat.PsyonixBot(
            name or "",
            loadout,
            skill_level,
        ),
        team,
        0,
    )


def get_human(team: int) -> flat.PlayerConfiguration:
    """
    Creates a `PlayerConfiguration` for a human player on the given team.
    """
    return flat.PlayerConfiguration(flat.Human(), team)


def load_script_config(path: Path | str) -> flat.ScriptConfiguration:
    """
    Reads the script toml file at the provided path and creates a `ScriptConfiguration` from it.
    """
    path = Path(path)
    with open(path, "rb") as f:
        config = tomllib.load(f)

    settings: dict[str, Any] = config["settings"]

    root_dir = path.parent
    if "root_dir" in settings:
        root_dir /= Path(__str(settings, "root_dir"))

    run_command = __str(settings, "run_command")
    if CURRENT_OS == OS.LINUX and "run_command_linux" in settings:
        run_command = __str(settings, "run_command_linux")

    return flat.ScriptConfiguration(
        __str(settings, "name"),
        str(root_dir),
        run_command,
        0,
        __str(settings, "agent_id"),
    )
