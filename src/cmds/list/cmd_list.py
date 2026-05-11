import logging

import pygit2 as pg
from result import Err, Ok, Result

from ...errors.not_bare_repo_err import NotBareRepoErr
from ...helpers.config_file import ensure_config_exists, read_config
from ...helpers.find_git import get_git_dir
from .args_list import ListArgs
from .result_list import ListWorktreesErr
from .worktree_info import WorktreeInfo


def list_worktrees(list_args: ListArgs) -> Result[list[WorktreeInfo], ListWorktreesErr]:
    log = logging.getLogger(__name__)

    git_dir = get_git_dir(list_args.current_working_dir)
    if not git_dir:
        log.warning("No bare git repository found; working_directory=%s", list_args.current_working_dir)
        return Err(NotBareRepoErr())

    log.info("Git repository found; git_dir=%s", git_dir)
    bare_repo: pg.Repository = pg.Repository(git_dir, flags=pg.enums.RepositoryOpenFlag.BARE)

    worktree_names: list[str] = bare_repo.list_worktrees()
    log.debug("Found worktrees; count=%s, names=%s", len(worktree_names), worktree_names)

    worktrees: list[WorktreeInfo] = []

    for name in worktree_names:
        try:
            wt: pg.Worktree = bare_repo.lookup_worktree(name)
        except (KeyError, pg.GitError) as e:
            log.warning("Failed to look up worktree, skipping; name=%s, error=%s", name, e)
            continue

        try:
            wt_repo: pg.Repository = pg.Repository(wt.path)
            actual_branch: str = wt_repo.head.shorthand
        except (KeyError, pg.GitError) as e:
            log.warning("Could not resolve branch for worktree; name=%s, error=%s", wt.name, e)
            actual_branch = wt.name  # fallback to name

        has_unmerged: bool = _has_unmerged_commits(bare_repo, git_dir, actual_branch)

        worktrees.append(
            WorktreeInfo(
                name=wt.name,
                path=wt.path,
                is_prunable=wt.is_prunable,
                has_unmerged_commits=has_unmerged,
            )
        )

    return Ok(worktrees)


def _has_unmerged_commits(repo: pg.Repository, git_dir: str, branch_name: str) -> bool:
    log = logging.getLogger(__name__)

    ensure_res = ensure_config_exists()
    match ensure_res:
        case Err(e):
            log.warning("Config not found, defaulting to main; error=%s", e)
            default_branch = "main"
        case Ok(config_path):
            read_res = read_config(config_path)
            match read_res:
                case Err(e):
                    log.warning("Failed to read config, defaulting to main; error=%s", e)
                    default_branch = "main"
                case Ok(config):
                    default_branch = config.get(git_dir, "default_branch_name", fallback="main")

    log.debug(
        "Checking unmerged commits; branch=%s, default_branch=%s",
        branch_name,
        default_branch,
    )

    try:
        branch_commit: pg.Commit = repo.lookup_reference(f"refs/heads/{branch_name}").peel(pg.Commit)
        default_commit: pg.Commit = repo.lookup_reference(f"refs/heads/{default_branch}").peel(pg.Commit)

        merge_base: pg.Oid = repo.merge_base(branch_commit.id, default_commit.id)

        return merge_base != branch_commit.id

    except (KeyError, pg.GitError) as e:
        log.warning("Could not resolve refs for merge check, skipping; error=%s", e)
        return False
