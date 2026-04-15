import click
import logging

from result import Err, Ok

from .errors.derived_branch_does_not_exist import DeriveBranchDoesNotExist
from .errors.no_fast_forward_merge import NoFastForwardMerge
from .errors.not_bare_repo_err import NotBareRepoErr
from .errors.worktree_creation_err import WorktreeCreationErr
from .helpers.logger import setup_logging
from .cmds.cmd_config import configure
from .cmds.add.cmd_add import add_worktree
from .cmds.add.args_add import AddArgs

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
# @click.argument("repository", help="The (possibly remote) <repository> to clone from.")
# @click.argument("directory", help="The name of a new directory to clone into.")
def clone(_repository: str, _directory: str):
    """
    Clone a repository as a bare-repo.\n
    Works as replacement for `git clone <repo> <directory>`.
    """

    click.echo("NOT IMPLEMENTED, YET!")


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

