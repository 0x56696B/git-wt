import logging
import shutil
from pathlib import Path

import pygit2 as pg
from result import Err, Ok, Result

from .args_rm import RmArgs
from .result_rm import RemoveWorktreeError
from ...errors.not_bare_repo_err import NotBareRepoErr
from ...errors.unmerged_changes_err import UnmergedChangesErr
from ...errors.worktree_not_found_err import WorktreeNotFoundErr
from ...errors.worktree_remove_err import WorktreeRemoveErr
from ...helpers.config_file import ensure_config_exists, read_config, remove_repo_entry
from ...helpers.find_git import get_git_dir


def remove_worktree(rm_args: RmArgs) -> Result[None, RemoveWorktreeError]:
    log = logging.getLogger(__name__)

    log.debug(
        "Attempting to remove worktrees; branch_names=%s, force=%s",
        rm_args.branch_names,
        rm_args.force,
    )

    git_dir = get_git_dir(rm_args.current_working_dir)
    if git_dir is None:
        log.warning(
            "No bare git repository found; working_directory=%s",
            rm_args.current_working_dir,
        )
        return Err(NotBareRepoErr())

    bare_repo: pg.Repository = pg.Repository(
        git_dir, flags=pg.enums.RepositoryOpenFlag.BARE
    )
    cwd: Path = Path(rm_args.current_working_dir).absolute()

    for branch_name in rm_args.branch_names:
        res = _remove_single(bare_repo, git_dir, cwd, branch_name, rm_args.force)
        match res:
            case Err(_) as err:
                return err
            case Ok(_):
                log.info(
                    "Successfully removed worktree; worktree_branch=%s", branch_name
                )
                pass

    remaining = bare_repo.list_worktrees()
    log.debug("Remaining worktrees after removal; count=%s", len(remaining))

    if not remaining:
        log.debug("No worktrees left, removing config entry; repo_path=%s", git_dir)

        repo_entry = remove_repo_entry(git_dir)
        match repo_entry:
            case Ok(_):
                pass
            case Err(_) as e:
                return e

    log.info("Worktrees removed successfully; branch_names=%s", rm_args.branch_names)

    return Ok(None)


def _remove_single(
    bare_repo: pg.Repository,
    git_dir: str,
    cwd: Path,
    branch_name: str,
    force: bool,
) -> Result[None, RemoveWorktreeError]:
    log = logging.getLogger(__name__)

    log.debug("Attempting to remove worktree; branch_name=%s", branch_name)

    try:
        worktree: pg.Worktree = bare_repo.lookup_worktree(branch_name)
    except (KeyError, pg.GitError):
        log.warning("Worktree not found; branch_name=%s", branch_name)
        return Err(WorktreeNotFoundErr())

    wt_path: Path = Path(worktree.path).absolute()

    if str(cwd).startswith(str(wt_path)):
        log.error(
            "Cannot remove the worktree you are currently in; worktree_path=%s", wt_path
        )
        return Err(WorktreeRemoveErr())

    if not force:
        unmerged = _has_unmerged_commits(bare_repo, git_dir, branch_name)
        if unmerged:
            log.error(
                "Branch has commits not in default branch, refusing removal; branch=%s. Use --force to override.",
                branch_name,
            )
            return Err(UnmergedChangesErr())

    log.debug("Removing worktree directory; path=%s", wt_path)

    try:
        shutil.rmtree(str(wt_path))
    except OSError as e:
        log.error("Failed to remove worktree directory; path=%s, error=%s", wt_path, e)
        return Err(WorktreeRemoveErr())

    try:
        worktree.prune(force)
        log.info("Worktree pruned; branch_name=%s", branch_name)
    except pg.GitError as e:
        log.error("Failed to prune worktree; branch_name=%s, error=%s", branch_name, e)
        return Err(WorktreeRemoveErr())

    return Ok(None)


def _has_unmerged_commits(repo: pg.Repository, git_dir: str, branch_name: str) -> bool:
    log = logging.getLogger(__name__)

    ensure_res = ensure_config_exists()
    match ensure_res:
        case Err(_):
            default_branch = "main"

        case Ok(config_path):
            read_res = read_config(config_path)
            match read_res:
                case Err(_):
                    default_branch = "main"

                case Ok(config):
                    default_branch = config.get(
                        git_dir, "default_branch_name", fallback="main"
                    )

    log.debug(
        "Checking unmerged commits; branch=%s, default_branch=%s",
        branch_name,
        default_branch,
    )

    try:
        branch_commit: pg.Commit = repo.lookup_reference(
            f"refs/heads/{branch_name}"
        ).peel(pg.Commit)
        default_commit: pg.Commit = repo.lookup_reference(
            f"refs/heads/{default_branch}"
        ).peel(pg.Commit)

        merge_base: pg.Oid = repo.merge_base(branch_commit.id, default_commit.id)

        # If merge base == branch tip, branch is fully contained in default
        return merge_base != branch_commit.id

    except (KeyError, pg.GitError) as e:
        log.warning("Could not resolve refs for merge check, skipping; error=%s", e)
        return False
