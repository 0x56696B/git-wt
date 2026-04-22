from ...errors.fetch_err import FetchErr
from ...errors.not_bare_repo_err import NotBareRepoErr
from ...errors.remote_branch_not_found_err import RemoteBranchNotFoundErr
from ...errors.worktree_already_exists import WorktreeAlreadyExistsErr
from ...errors.worktree_creation_err import WorktreeCreationErr

PullWorktreeErr = NotBareRepoErr | WorktreeCreationErr | WorktreeAlreadyExistsErr | RemoteBranchNotFoundErr | FetchErr
