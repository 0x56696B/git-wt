from ...errors.not_bare_repo_err import NotBareRepoErr
from ...errors.config_read_err import ConfigReadErr
from ...errors.config_write_err import ConfigWriteErr
from ...errors.config_perm_err import ConfigPermErr


ConfigError = NotBareRepoErr | ConfigReadErr | ConfigWriteErr | ConfigPermErr
