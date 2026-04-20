from ...errors.path_cannot_be_file import PathCannotBeFile
from ...errors.directory_not_empty import DirectoryNotEmpty
from ...errors.worktree_creation_err import WorktreeCreationErr


CloneRespositoryErr = PathCannotBeFile | DirectoryNotEmpty | WorktreeCreationErr
