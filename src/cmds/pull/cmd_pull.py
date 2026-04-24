import logging
from pathlib import Path

import pygit2 as pg
from result import Err, Ok, Result

from ...errors.fetch_err import FetchErr
from ...errors.not_bare_repo_err import NotBareRepoErr
from ...errors.remote_branch_not_found_err import RemoteBranchNotFoundErr
from ...errors.worktree_already_exists import WorktreeAlreadyExistsErr
from ...errors.worktree_creation_err import WorktreeCreationErr
from ...helpers.auth_agent_callback import AuthAgentCallback
from ...helpers.find_git import get_git_dir
from .args_pull import PullArgs
from .result_pull import PullWorktreeErr


def pull_worktree(pull_args: PullArgs) -> Result[None, PullWorktreeErr]:
    log = logging.getLogger(__name__)

    sanitized_branch_name: str = pull_args.branch_name.replace("/", "-")
    current_path: str = pull_args.current_working_dir

    log.debug(
        "Attempting to pull worktree; branch_name=%s, sanitized_branch_name=%s, current_path=%s",
        pull_args.branch_name,
        sanitized_branch_name,
        current_path,
    )

    git_dir = get_git_dir(current_path)
    if not git_dir:
        log.warning("This isn't a bare git repository; branch_name=%s, current_path=%s", pull_args.branch_name, current_path)
        return Err(NotBareRepoErr())

    log.info("Git repository found; git_dir=%s", git_dir)
    bare_repo: pg.Repository = pg.Repository(git_dir, flags=pg.enums.RepositoryOpenFlag.BARE)

    log.debug("Repository opened; repository=%s", bare_repo)

    if not bare_repo.is_bare:
        log.warning("This isn't a bare git repository; branch_name=%s, current_path=%s", pull_args.branch_name, current_path)
        return Err(NotBareRepoErr())

    try:
        log.debug("Fetching branch from origin; branch_name=%s", pull_args.branch_name)
        remote: pg.Remote = bare_repo.remotes["origin"]
        _ = remote.fetch(refspecs=[f"refs/heads/{pull_args.branch_name}:refs/heads/{pull_args.branch_name}"], callbacks=AuthAgentCallback())
        log.info("Fetched branch from origin; branch_name=%s", pull_args.branch_name)
    except (KeyError, pg.GitError) as e:
        log.error("Failed to fetch from origin; branch_name=%s, error=%s", pull_args.branch_name, e)
        return Err(FetchErr())

    try:
        branch_ref: pg.Reference = bare_repo.lookup_reference(f"refs/heads/{pull_args.branch_name}")
        log.debug("Branch ref resolved; branch_name=%s, target=%s", pull_args.branch_name, branch_ref.target)
    except (KeyError, pg.GitError) as e:
        log.error("Branch not found after fetch; branch_name=%s, error=%s", pull_args.branch_name, e)
        return Err(RemoteBranchNotFoundErr())

    wt_path: Path = Path(git_dir, sanitized_branch_name).absolute()

    log.debug("Preparing to create worktree; worktree_path=%s, worktree_name=%s, repository=%s", wt_path, sanitized_branch_name, bare_repo)

    try:
        new_worktree: pg.Worktree = bare_repo.add_worktree(sanitized_branch_name, str(wt_path), branch_ref)
        log.info("Successfully created a worktree; worktree_name=%s, branch_name=%s", new_worktree.name, pull_args.branch_name)
    except OSError:
        log.error("Worktree creation failed; worktree_path=%s, worktree_name=%s, repository=%s", wt_path, sanitized_branch_name, bare_repo)
        return Err(WorktreeCreationErr())
    except pg.AlreadyExistsError:
        log.error(
            "Worktree with the same name already exists; worktree_path=%s, worktree_name=%s, repository=%s",
            wt_path,
            sanitized_branch_name,
            bare_repo,
        )
        return Err(WorktreeAlreadyExistsErr())

    return Ok(None)
