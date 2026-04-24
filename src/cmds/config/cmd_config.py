import logging

from result import Err, Ok, Result

from .args_config import ConfigArgs
from .result_config import ConfigError
from ...errors.not_bare_repo_err import NotBareRepoErr
from ...helpers.config_file import (
    ensure_config_exists,
    get_list_value,
    read_config,
    set_list_value,
    write_config_file,
)
from ...helpers.find_git import get_git_dir


def configure(config_args: ConfigArgs) -> Result[None, ConfigError]:
    log = logging.getLogger(__name__)

    log.debug("Configuring; config_args=%s", config_args)

    repo_path = get_git_dir(config_args.current_working_dir)
    if repo_path is None:
        return Err(NotBareRepoErr())

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

    if config_args.list:
        if config.has_section(repo_path):
            log.info(
                "add_commands = %s", get_list_value(config, repo_path, "add_commands")
            )
            log.info(
                "rm_commands = %s", get_list_value(config, repo_path, "rm_commands")
            )
            log.info(
                "exclude_files = %s", get_list_value(config, repo_path, "exclude_files")
            )
            log.info(
                "default_branch_name = %s",
                config.get(repo_path, "default_branch_name", fallback=""),
            )
        else:
            log.info("No configuration found for %s", repo_path)

        return Ok(None)

    if not config.has_section(repo_path):
        config.add_section(repo_path)

    set_list_value(config, repo_path, "add_commands", config_args.add_commands)
    set_list_value(config, repo_path, "rm_commands", config_args.remove_commands)
    set_list_value(config, repo_path, "exclude_files", config_args.copy_exclude)

    if config_args.default_branch_name:
        config.set(repo_path, "default_branch_name", config_args.default_branch_name)

    return write_config_file(config, config_path)
