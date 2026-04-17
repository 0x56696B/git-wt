import click
import logging

from result import Err, Ok

from .errors.path_cannot_be_file import PathCannotBeFile
from .errors.directory_not_empty import DirectoryNotEmpty
from .errors.derived_branch_does_not_exist import DeriveBranchDoesNotExist
from .errors.no_fast_forward_merge import NoFastForwardMerge
from .errors.not_bare_repo_err import NotBareRepoErr
from .errors.worktree_creation_err import WorktreeCreationErr

from .helpers.logger import setup_logging
from .cmds.cmd_config import configure

from .cmds.add.cmd_add import add_worktree
from .cmds.add.args_add import AddArgs

from .cmds.clone.cmd_clone import clone_repository
from .cmds.clone.args_clone import CloneArgs


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

        case Err(WorktreeCreationErr()):
            log.error("An error occured while trying to create the new branch. Please, try again.")

        case Err(DeriveBranchDoesNotExist()):
            log.error("The derived branch does not exist. A worktree from it cannot be created.")

        case Err(NoFastForwardMerge()):
            log.error("The derived branch has conflitcs and cannot fast-forward changes from origin.")

        case Err(_):
            log.fatal("Something has gone horribly wrong. Aporting immediately!")

            exit(-1)

        case Ok(None):
            log.info("Successfully created new worktree")


@cli.command()
@click.option(
    "--add-commands",
    type=str,
    multiple=True,
    metavar="<CMD>",
    help="Commands to run after successful worktree creation. Automatically ran after `git wt add`.")
@click.option(
    "--remove-commands",
    type=str,
    multiple=True,
    metavar="<CMD>",
    help="Commands to run after successful worktree removal. Automatically ran after `git wt rm`.")
@click.option(
    "--copy-exclude",
    type=str,
    multiple=True,
    metavar="<CMD>",
    help="Files to exclude when copying after worktree creation.")
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
def config(add_commands: str, remove_commands: str, copy_exclude: str, list: bool):
    configure(add_commands, remove_commands, copy_exclude, list)


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

    clone_args: CloneArgs = CloneArgs(
        repository_link=repository,
        dest=directory
    )

    clone_res = clone_repository(clone_args)

    log.debug("Repository cloning result; result=%s", clone_res)

    match clone_res:
        case Ok(repo):
            log.info("Repository clonned successfully; repo_workdir=%s, repo_path=%s", repo.workdir, repo.path)

            exit(0)

        case Err(PathCannotBeFile()):
            log.error("The provided path cannot be a file.")

            exit(4)

        case Err(DirectoryNotEmpty()):
            log.error("Direcotry is not empty. Cloning in it may overwrite files")

            exit(5)

        case Err(_):
            log.fatal("Something has gone horribly wrong. Aporting immediately!")

            exit(1)



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

