from ...errors.path_cannot_be_file import PathCannotBeFile
from ...errors.directory_not_empty import DirectoryNotEmpty


CloneRespositoryErr = PathCannotBeFile | DirectoryNotEmpty
