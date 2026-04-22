import logging
import os
import pygit2 as pg

from pathlib import Path
from result import Err, Ok, Result

from ...errors.path_cannot_be_file import PathCannotBeFile
from ...errors.directory_not_empty import DirectoryNotEmpty
from ...errors.worktree_creation_err import WorktreeCreationErr
from ...helpers.auth_agent_callback import AuthAgentCallback

from .args_clone import CloneArgs
from .result_clone import CloneRepositoryErr


def clone_repository(clone_args: CloneArgs) -> Result[pg.Repository, CloneRepositoryErr]:
    log = logging.getLogger(__name__)

    log.debug("Attempting to create a repository; url=%s, dest=%s", clone_args.repository_link, clone_args.dest.absolute())

    if clone_args.dest.is_file(follow_symlinks=True):
        return Err(PathCannotBeFile())

    if not clone_args.dest.exists(follow_symlinks=True):
        os.makedirs(clone_args.dest, exist_ok=True)

    if any(os.scandir(clone_args.dest)):
        return Err(DirectoryNotEmpty())

    repo: pg.Repository | None = None
    try:
        repo = pg.clone_repository(
            url=clone_args.repository_link,
            path=str(clone_args.dest.absolute()),
            bare=True,
            proxy=True,
            callbacks=AuthAgentCallback()
        )

    except pg.GitError as e:
        log.fatal("An error occured; error=%s", e)
        return Err(DirectoryNotEmpty())

    assert Path(repo.path).absolute() == clone_args.dest.absolute(), "A BARE repository must be created at the designated path"

    default_branch = _get_default_branch(repo)

    log.debug("Detected default branch; branch=%s", default_branch)

    wt_res = _create_default_worktree(repo, clone_args.dest.absolute(), default_branch)
    match wt_res:
        case Err(_) as err:
            return err
        case Ok(_):
            pass

    return Ok(repo)


def _get_default_branch(repo: pg.Repository) -> str:
    log = logging.getLogger(__name__)

    try:
        return repo.head.shorthand

    except (pg.GitError, KeyError) as e:
        log.warning("Could not determine default branch, falling back to 'main'; error=%s", e)
        return "main"


def _create_default_worktree(repo: pg.Repository, dest: Path, branch_name: str) -> Result[None, WorktreeCreationErr]:
    log = logging.getLogger(__name__)

    wt_path = dest / branch_name

    log.debug("Attempting to create a default worktree; branch=%s, path=%s", branch_name, wt_path)

    try:
        ref = repo.lookup_reference(f"refs/heads/{branch_name}")
        _new_wt = repo.add_worktree(branch_name, str(wt_path), ref)
    except (pg.GitError, OSError) as e:
        log.error("Failed to create default worktree; branch=%s, error=%s", branch_name, e)
        return Err(WorktreeCreationErr())

    log.info("Created default worktree; branch=%s, path=%s", branch_name, wt_path)

    return Ok(None)
