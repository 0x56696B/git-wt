import os
import click
import logging

from pathlib import Path
from result import Err, Ok

from .errors.path_cannot_be_file import PathCannotBeFile
from .errors.directory_not_empty import DirectoryNotEmpty
from .errors.derived_branch_does_not_exist import DeriveBranchDoesNotExist
from .errors.no_fast_forward_merge import NoFastForwardMerge
from .errors.not_bare_repo_err import NotBareRepoErr
from .errors.worktree_creation_err import WorktreeCreationErr
from .errors.config_read_err import ConfigReadErr
from .errors.config_write_err import ConfigWriteErr
from .errors.config_perm_err import ConfigPermErr
from .errors.unmerged_changes_err import UnmergedChangesErr
from .errors.worktree_not_found_err import WorktreeNotFoundErr
from .errors.worktree_remove_err import WorktreeRemoveErr

from .exit_codes import ExitCode
from .helpers.logger import setup_logging
from .helpers.config_file import ensure_repo_entry

from .cmds.add.cmd_add import add_worktree
from .cmds.add.args_add import AddArgs

from .cmds.clone.cmd_clone import clone_repository
from .cmds.clone.args_clone import CloneArgs

from .cmds.config.cmd_config import configure
from .cmds.config.args_config import ConfigArgs

from .cmds.rm.cmd_rm import remove_worktree
from .cmds.rm.args_rm import RmArgs


@click.group()
@click.version_option("0.1.0")
def cli():
    """A git-worktree extension to make using worktrees a pain of the past"""
    setup_logging()


@cli.command()
@click.argument("NEW_BRANCH_NAME", type=str)
@click.argument("DERIVE_FROM_BRANCH", type=str, required=False)
@click.option("--force", "-f", is_flag=True, default=False, help="Force checkout, even if branch already exists locally")
@click.option("--exclude", "-e", type=str, help="""
Exclude files from being copied over. Provide a comma-seperated list

Example: `--exclude="node_modules,dist,target,bin"`

WARNING: This can override the config file
""")
def add(new_branch_name: str, derive_from_branch: str, exclude: list[str]=[], force: bool=False):
    """
    Create a worktree

    NOTE: This copies over ONLY files configured for the current repository in the git-wt config

    NOTE: Slashes(`/`) in the branch name will be replaced with dash(`-`) to avoid directory nesting
    """

    # Take these from config
    should_nest_dirs: bool = False
    exclude_files_from_copy: list[str] = exclude or []

    add_args: AddArgs = AddArgs(
        new_branch_name,
        derive_from_branch,
        should_nest_dirs,
        exclude_files_from_copy,
        force
    )

    worktree_creaton_res = add_worktree(add_args)

    log = logging.getLogger(__name__)
    log.debug("Repository creation result; result=%s", worktree_creaton_res)

    match worktree_creaton_res:
        case Err(NotBareRepoErr()):
            log.error("Cannot find a BARE git repository in the current working directory.")
            exit(ExitCode.ERR_NOT_BARE_REPO)

        case Err(WorktreeCreationErr()):
            log.error("An error occured while trying to create the new branch. Please, try again.")
            exit(ExitCode.ERR_WORKTREE)

        case Err(DeriveBranchDoesNotExist()):
            log.error("The derived branch does not exist. A worktree from it cannot be created.")
            exit(ExitCode.ERR_BRANCH_MISSING)

        case Err(NoFastForwardMerge()):
            log.error("The derived branch has conflitcs and cannot fast-forward changes from origin.")
            exit(ExitCode.ERR_NO_FF_MERGE)

        case Err(_):
            log.fatal("Something has gone horribly wrong. Aporting immediately!")
            exit(ExitCode.ERR_GENERAL)

        case Ok(None):
            log.info("Successfully created new worktree")
            exit(ExitCode.SUCCESS)


@cli.command()
@click.option(
    "--add-command",
    type=str,
    multiple=True,
    metavar="<CMD>",
    help="Command to run after successful worktree creation. Can be repeated for multiple commands. Automatically ran after `git wt add`.")
@click.option(
    "--remove-command",
    type=str,
    multiple=True,
    metavar="<CMD>",
    help="Command to run after successful worktree removal. Can be repeated for multiple commands. Automatically ran after `git wt rm`.")
@click.option(
    "--exclude", "-e",
    type=str,
    multiple=True,
    metavar="<GLOB>",
    help="Glob pattern of files to exclude when copying after worktree creation. Can be repeated to specify multiple patterns.")
@click.option(
    "--default-branch",
    type=str,
    default="",
    metavar="<BRANCH>",
    help="Default branch name to derive new worktrees from.")
@click.option(
    "--list", "-l",
    is_flag=True,
    default=False,
    help="""
        List configured entries.

        NOTE: This command will store different configuration for each repository.

        Example: ["node_modules", "cache"]

        The `git wt add` wouldn't need `--exclude "node_modules" --exclude "cache"` every time it's ran in the configured repo.
    """)
def config(add_command: tuple[str, ...], remove_command: tuple[str, ...], exclude: tuple[str, ...], default_branch: str, list: bool):
    log = logging.getLogger(__name__)

    config_args: ConfigArgs = ConfigArgs(
        current_working_dir=os.getcwd(),
        add_commands=add_command,
        remove_commands=remove_command,
        copy_exclude=exclude,
        default_branch_name=default_branch,
        list=list
    )

    config_res = configure(config_args)

    log.debug("Config result; result=%s", config_res)

    match config_res:
        case Err(NotBareRepoErr()):
            log.error("Cannot find a BARE git repository in the current working directory.")
            exit(ExitCode.ERR_NOT_BARE_REPO)

        case Err(ConfigReadErr()):
            log.error("Failed to read the config file.")
            exit(ExitCode.ERR_CONFIG_READ)

        case Err(ConfigWriteErr()):
            log.error("Failed to write to the config file.")
            exit(ExitCode.ERR_CONFIG_WRITE)

        case Err(ConfigPermErr()):
            log.error("Insufficient permissions to access the config file.")
            exit(ExitCode.ERR_CONFIG_PERM)

        case Err(_):
            log.fatal("Something has gone horribly wrong. Aporting immediately!")
            exit(ExitCode.ERR_GENERAL)

        case Ok(None):
            log.info("Config updated successfully")
            exit(ExitCode.SUCCESS)


@cli.command()
@click.argument("REPOSITORY", required=True, type=str)
@click.argument("DIRECTORY", required=True, type=str)
def clone(repository: str, directory: str):
    """
    Clone a repository as a bare-repo.\n
    Works as replacement for `git clone <repo> <directory>`.\n
    Will create the directory, if it doesn't exist.
    """

    log = logging.getLogger(__name__)

    dest = Path(directory)
    log.debug("Created destination; dest=%s", dest.absolute())

    entry_res = ensure_repo_entry(dest)
    match entry_res:
        case Err(ConfigReadErr()):
            log.error("Failed to read the config file.")

            exit(ExitCode.ERR_CONFIG_READ)

        case Err(ConfigWriteErr()):
            log.error("Failed to write to the config file.")

            exit(ExitCode.ERR_CONFIG_WRITE)

        case Err(ConfigPermErr()):
            log.error("Insufficient permissions to access the config file.")

            exit(ExitCode.ERR_CONFIG_PERM)

        case Err(_):
            log.fatal("Something has gone horribly wrong. Aporting immediately!")
            exit(ExitCode.ERR_GENERAL)

        case Ok(_):
            pass

    clone_args: CloneArgs = CloneArgs(
        repository_link=repository,
        dest=dest
    )

    clone_res = clone_repository(clone_args)

    log.debug("Repository cloning result; result=%s", clone_res)

    match clone_res:
        case Err(PathCannotBeFile()):
            log.error("The provided path cannot be a file.")
            exit(ExitCode.ERR_PATH_IS_FILE)

        case Err(DirectoryNotEmpty()):
            log.error("Direcotry is not empty. Cloning in it may overwrite files")
            exit(ExitCode.ERR_DIR_NOT_EMPTY)

        case Err(WorktreeCreationErr()):
            log.error("Repository cloned but failed to create the default worktree.")
            exit(ExitCode.ERR_WORKTREE)

        case Err(_):
            log.fatal("Something has gone horribly wrong. Aporting immediately!")
            exit(ExitCode.ERR_GENERAL)

        case Ok(repo):
            log.info("Repository clonned successfully; repo_workdir=%s, repo_path=%s", repo.workdir, repo.path)
            exit(ExitCode.SUCCESS)


@cli.command()
@click.argument("BRANCH_NAMES", nargs=-1, required=True, type=str)
@click.option("--force", "-f", is_flag=True, default=False, help="Remove even if the branch has commits not present in the default branch.")
def rm(branch_names: tuple[str, ...], force: bool):
    """Remove one or more worktrees."""

    log = logging.getLogger(__name__)

    rm_args: RmArgs = RmArgs(
        branch_names=branch_names,
        current_working_dir=os.getcwd(),
        force=force
    )

    rm_res = remove_worktree(rm_args)

    log.debug("Worktree removal result; result=%s", rm_res)

    match rm_res:
        case Err(NotBareRepoErr()):
            log.error("Cannot find a BARE git repository in the current working directory.")
            exit(ExitCode.ERR_NOT_BARE_REPO)

        case Err(WorktreeNotFoundErr()):
            log.error("Worktree not found.")
            exit(ExitCode.ERR_WORKTREE_MISSING)

        case Err(UnmergedChangesErr()):
            log.error("Branch has commits not in the default branch. Use --force to override.")
            exit(ExitCode.ERR_UNMERGED)

        case Err(WorktreeRemoveErr()):
            log.error("Failed to remove worktree.")
            exit(ExitCode.ERR_WORKTREE)

        case Err(_):
            log.fatal("Something has gone horribly wrong. Aporting immediately!")
            exit(ExitCode.ERR_GENERAL)

        case Ok(None):
            log.info("Worktrees successfully cleaned up; branch_names=%s", branch_names)
            exit(ExitCode.SUCCESS)


@cli.command()
def switch():
    """
    Execute switch worktree commands.\n
    Commands configurable through `git wt config`.

    Example:\n
        My project has docker, so running `docker compose up -d` spawns containers.\n
        I also need to stop those containers in one branch to start development in another branch, because of container name collisions\n
        What if I can just define a swtich command that I can run while in `feature-branch-X` to stop the containers in `main`?\n
        This command can do just that. Configurable.
    """

    click.echo("NOT IMPLEMENTED, YET!")


if __name__ == "__main__":
    cli()

