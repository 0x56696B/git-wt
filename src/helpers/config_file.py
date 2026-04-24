import configparser
import logging
import os
from pathlib import Path

from result import Err, Ok, Result

from ..errors.config_perm_err import ConfigPermErr
from ..errors.config_read_err import ConfigReadErr
from ..errors.config_write_err import ConfigWriteErr

CONFIG_PATH = Path.home() / ".gitconfig_wt"


def ensure_config_exists() -> Result[Path, ConfigWriteErr | ConfigPermErr]:
    log = logging.getLogger(__name__)

    if not CONFIG_PATH.exists():
        log.debug("Config not found, creating; path=%s", CONFIG_PATH)

        try:
            CONFIG_PATH.touch()

            log.debug("Config successfully created; path=%s", CONFIG_PATH)
        except OSError as e:
            log.error("Failed to create config; error=%s", e)
            return Err(ConfigWriteErr())

        return Ok(CONFIG_PATH)

    if not os.access(CONFIG_PATH, os.R_OK):
        log.error("No read permission on config; path=%s", CONFIG_PATH)

        return Err(ConfigPermErr())

    log.debug("Config exists and can be read successfully; config_path=%s", CONFIG_PATH)

    return Ok(CONFIG_PATH)


def read_config(path: Path) -> Result[configparser.RawConfigParser, ConfigReadErr]:
    log = logging.getLogger(__name__)

    log.debug("Attempting to read raw config; config_path=%s", path)

    try:
        config = configparser.RawConfigParser()

        read_files = config.read(path)

        log.debug("Successfully read files; files_read=%s", read_files)

        return Ok(config)

    except configparser.Error as e:
        log.error("Failed to parse config; error=%s", e)
        return Err(ConfigReadErr())


def set_list_value(
    config: configparser.RawConfigParser,
    section: str,
    key: str,
    values: tuple[str, ...],
) -> None:
    if not values:
        return

    config.set(section, key, "\n" + "\n".join(values))


def get_list_value(config: configparser.RawConfigParser, section: str, key: str) -> list[str]:
    raw = config.get(section, key, fallback="")

    return [line.strip() for line in raw.splitlines() if line.strip()]


def write_config_file(config: configparser.RawConfigParser, path: Path) -> Result[None, ConfigWriteErr]:
    log = logging.getLogger(__name__)

    try:
        with open(path, "w") as f:
            for section in config.sections():
                _ = f.write(f"[{section}]\n")

                for key, value in config.items(section):
                    lines = [line for line in value.splitlines() if line.strip()]

                    if not lines:
                        _ = f.write(f"    {key} =\n")
                    elif len(lines) == 1:
                        _ = f.write(f"    {key} = {lines[0]}\n")
                    else:
                        _ = f.write(f"    {key} =\n")
                        for line in lines:
                            _ = f.write(f"        {line}\n")

                _ = f.write("\n")

        return Ok(None)

    except OSError as e:
        log.error("Failed to write config; error=%s", e)
        return Err(ConfigWriteErr())


def remove_repo_entry(
    repo_path: str,
) -> Result[None, ConfigReadErr | ConfigWriteErr | ConfigPermErr]:
    log = logging.getLogger(__name__)

    ensure_res = ensure_config_exists()
    match ensure_res:
        case Err(_) as err:
            return err

        case Ok(config_path):
            pass

    read_res = read_config(config_path)
    match read_res:
        case Err(_) as err:
            return err

        case Ok(config):
            pass

    if config.has_section(repo_path):
        config.remove_section(repo_path)

        log.debug("Removed config section; repo_path=%s", repo_path)

        return write_config_file(config, config_path)

    return Ok(None)


def ensure_repo_entry(
    repo_path: Path,
) -> Result[None, ConfigReadErr | ConfigWriteErr | ConfigPermErr]:
    """Ensure a section exists in the config for repo_path. Called after clone."""
    ensure_res = ensure_config_exists()
    match ensure_res:
        case Err(_) as err:
            return err

        case Ok(config_path):
            pass

    read_res = read_config(config_path)
    match read_res:
        case Err(_) as err:
            return err
        case Ok(config):
            pass

    if not config.has_section(str(repo_path.absolute())):
        config.add_section(str(repo_path.absolute()))
        return write_config_file(config, config_path)

    return Ok(None)
