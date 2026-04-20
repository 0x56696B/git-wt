from fnmatch import fnmatch
import logging
import os
import pygit2 as pg

from result import Result, Ok, Err
from shutil import copy2, copytree
from pathlib import Path
from uuid import uuid4

from .args_add import AddArgs
from .result_add import AddWorktreeError

from ...errors.no_fast_forward_merge import NoFastForwardMerge
from ...errors.worktree_already_exists import WorktreeAlreadyExistsErr
from ...errors.derived_branch_does_not_exist import DeriveBranchDoesNotExist
from ...helpers.find_git import get_git_dir
from ...errors.not_bare_repo_err import NotBareRepoErr
from ...errors.worktree_creation_err import WorktreeCreationErr


def add_worktree(add_args: AddArgs) -> Result[None, AddWorktreeError]:
    log = logging.getLogger(__name__)

    branch_name: str = add_args.new_branch_name if add_args.should_nest_dirs else add_args.new_branch_name.replace('/', '-')
    current_path: str = os.getcwd()

    log.debug("Attempting to find git dir; should_nest_dirs=%s, branch_path=%s, current_path=%s", add_args.should_nest_dirs, branch_name, current_path)

    git_dir = get_git_dir(current_path)
    if not git_dir:
        log.warning("This isn't a bare git repository; should_nest_dirs=%s, branch_path=%s, current_path=%s", add_args.should_nest_dirs, branch_name, current_path)
        return Err(NotBareRepoErr())

    derived_branch_exists: Path = Path(git_dir, add_args.derive_from_branch)
    if not derived_branch_exists.exists(follow_symlinks=True):
        log.warning("Derived branch does not exist; derived_branch_path=%s", str( derived_branch_exists.absolute ))
        return Err(DeriveBranchDoesNotExist())

    # TODO: Specify the repo to be based on the derived_branch
    log.info("Git repository found; git_dir=%s", git_dir)
    bare_repo: pg.Repository = pg.Repository(git_dir, flags=pg.enums.RepositoryOpenFlag.BARE)

    log.debug("Repository opened; repository=%s", bare_repo)

    # Technically shouldn't be hittable, as get_git_dir checks for that
    if not bare_repo.is_bare:
        log.warning("This isn't a bare git repository; should_nest_dirs=%s, branch_path=%s, current_path=%s", add_args.should_nest_dirs, branch_name, current_path)
        return Err(NotBareRepoErr())

    # TODO: Check if this fetches main branch, if configured
    # remote = repo.remotes["origin"]
    # transfer_progress = remote.fetch(prune=FetchPrune.NO_PRUNE, proxy=True)
    #
    # log.info("Fetched commits from origin; num_fetched_commits=%s", transfer_progress.total_deltas)

    remote_branch = bare_repo.lookup_reference(f"refs/heads/{add_args.derive_from_branch}").peel(pg.Commit)
    analysis, _ = bare_repo.merge_analysis(remote_branch.id)

    log.debug("Derived branch info; derive_branch_ref=%s, analysis=%s", remote_branch.id, analysis)

    if analysis & pg.GIT_MERGE_ANALYSIS_UP_TO_DATE:
        log.info("Derived branch already up to date; derive_from_branch=%s", add_args.derive_from_branch)

    elif analysis & pg.GIT_MERGE_ANALYSIS_FASTFORWARD:
        # NOTE: Untested!
        # Move HEAD and working tree forward
        _ = bare_repo.checkout_tree(treeish=bare_repo.get(remote_branch.id))  # pyright: ignore[reportUnknownMemberType]
        bare_repo.lookup_reference(f"refs/heads/{add_args.derive_from_branch}").set_target(remote_branch.id)
        bare_repo.head.set_target(remote_branch.id)

        log.info("Fast-forwarded ref branch; fast_forwarded=%s", remote_branch.id)

    else:
        # True merge required — pygit2 can do it but you'd need to handle conflicts
        return Err(NoFastForwardMerge())


    new_worktree: pg.Worktree | None = None
    wt_path = Path(git_dir, branch_name).absolute()

    log.debug("Preparing to create worktree; worktree_path=%s, worktree_name=%s, repository=%s", wt_path, branch_name, bare_repo)

    try:
        new_worktree = bare_repo.add_worktree(branch_name, wt_path)

        log.info("Successully created a worktree; worktree_name=%s, branch_name=%s", new_worktree.name, branch_name)

    except OSError:
        log.error("Worktree opening failed; worktree_path=%s, worktree_name=%s, repository=%s", wt_path, branch_name, bare_repo)

        return Err(WorktreeCreationErr())

    except pg.AlreadyExistsError:
        log.error("Worktree with the same name already exists; worktree_path=%s, worktree_name=%s, repository=%s", wt_path, branch_name, bare_repo)

        return Err(WorktreeAlreadyExistsErr())


    assert new_worktree is not None, "The new worktree must be created. Something wasn not handled correctly"
    assert new_worktree.name == branch_name, "Worktree name must equal to the branch name provided"
    assert new_worktree.path == str(wt_path), "The path of the worktree must be the same as the given path for worktree creation"


    derive_branch_path: Path = Path(git_dir, add_args.derive_from_branch)
    log.info("Preparing for file coping; copy_from=%s, copy_to=%s", str( derive_branch_path ), new_worktree.path)

    derived_repo = pg.Repository(derive_branch_path)
    log.debug("Derived repository opened; derived_repository=%s; derived_repo_workdir=%s", derived_repo, derived_repo.workdir)

    git_ignored_files = [Path(derived_repo.workdir, ignored) for ignored in derived_repo.status(untracked_files="no", ignored=True)]
    git_ignored_filtered_files = [ignored_file for ignored_file in git_ignored_files if not any(fnmatch(ignored_file.name, excluded_glob) for excluded_glob in add_args.exclude)]

    log.debug("Found git ignored files from derived branch; git_ignored_files=%s", git_ignored_filtered_files)

    try:
        for path in git_ignored_filtered_files:
            cp_res: str | None = None

            if path.is_file() and path.name != ".git":
                cp_res = copy2(str(path), new_worktree.path, follow_symlinks=True)

            elif path.is_dir():
                cp_res = copytree(str(path), new_worktree.path, symlinks=True, dirs_exist_ok=True)

            else:
                log.debug("Neither a dir, nor a file, that should be copied; file=%s", path)

            log.info("Copied ignored file; file=%s", cp_res)

    except OSError as os_err:
        log.error("A copy error occured; err=%s", os_err)

    return Ok(None)
