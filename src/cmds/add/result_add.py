from ...errors.derived_branch_does_not_exist import DeriveBranchDoesNotExist
from ...errors.no_fast_forward_merge import NoFastForwardMerge
from ...errors.not_bare_repo_err import NotBareRepoErr
from ...errors.worktree_already_exists import WorktreeAlreadyExistsErr
from ...errors.worktree_creation_err import WorktreeCreationErr

AddWorktreeError = (
    NotBareRepoErr
    | WorktreeCreationErr
    | WorktreeAlreadyExistsErr
    | DeriveBranchDoesNotExist
    | NoFastForwardMerge
)
