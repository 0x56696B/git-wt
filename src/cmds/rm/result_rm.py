from ...errors.config_perm_err import ConfigPermErr
from ...errors.config_read_err import ConfigReadErr
from ...errors.config_write_err import ConfigWriteErr
from ...errors.not_bare_repo_err import NotBareRepoErr
from ...errors.unmerged_changes_err import UnmergedChangesErr
from ...errors.worktree_not_found_err import WorktreeNotFoundErr
from ...errors.worktree_remove_err import WorktreeRemoveErr

RemoveWorktreeError = (
    NotBareRepoErr
    | WorktreeNotFoundErr
    | WorktreeRemoveErr
    | ConfigReadErr
    | ConfigWriteErr
    | ConfigPermErr
    | UnmergedChangesErr
)
