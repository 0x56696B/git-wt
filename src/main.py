import click

from .cmds.cmd_config import configure

@click.group()
@click.version_option("0.1.0")
def cli():
    """A git-worktree extension to make using worktrees a pain of the past"""
    pass


@cli.command()
@click.argument("NEW_BRANCH_NAME", type=str)
@click.option("--force", "-f", is_flag=True, default=False, help="Force checkout, even if branch already exists locally")
@click.option("--exclude", "-e", type=str, help="""
Exclude files from being copied over. Provide a comma-seperated list

Example: `--exclude="node_modules,dist,target,bin"`

WARNING: This can override the config file
""")
def add(new_branch_name: str, exclude: list[str]=[],force: bool=False):
    """
    Create a worktree

    NOTE: This copies over ONLY files configured for the current repository in the git-wt config

    NOTE: Slashes(`/`) in the branch name will be replaced with dash(`-`) to avoid directory nesting
    """

    print("in add cmd: ", new_branch_name, force, exclude)

    click.echo("NOT IMPLEMENTED, YET!")


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

