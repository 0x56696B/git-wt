from ...errors.config_perm_err import ConfigPermErr
from ...errors.config_read_err import ConfigReadErr
from ...errors.config_write_err import ConfigWriteErr
from ...errors.not_bare_repo_err import NotBareRepoErr

ConfigError = NotBareRepoErr | ConfigReadErr | ConfigWriteErr | ConfigPermErr
