from ...errors.config_perm_err import ConfigPermErr
from ...errors.config_read_err import ConfigReadErr
from ...errors.config_write_err import ConfigWriteErr
from ...errors.destroy_err import DestroyErr
from ...errors.directory_not_found_err import DirectoryNotFoundErr
from ...errors.not_bare_repo_err import NotBareRepoErr

DestroyRepoError = NotBareRepoErr | DirectoryNotFoundErr | DestroyErr | ConfigReadErr | ConfigWriteErr | ConfigPermErr
