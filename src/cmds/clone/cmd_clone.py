import logging
import os
import pygit2 as pg

from pathlib import Path
from result import Err, Ok, Result

from ...errors.path_cannot_be_file import PathCannotBeFile
from ...helpers.auth_agent_callback import AuthAgentCallback
from ...errors.directory_not_empty import DirectoryNotEmpty

from .args_clone import CloneArgs
from .result_clone import CloneRespositoryErr


def clone_repository(clone_args: CloneArgs) -> Result[pg.Repository, CloneRespositoryErr]:
    log = logging.getLogger(__name__)

    log.debug("Attempting to create a repository; url=%s, dest=%s", clone_args.repository_link, clone_args.dest)

    dest = Path(clone_args.dest)
    log.debug("Created a destination path; dest=%s", dest.absolute())

    if dest.is_file(follow_symlinks=True):
        return Err(PathCannotBeFile())

    if not dest.exists(follow_symlinks=True):
        os.makedirs(dest, exist_ok=True)

    if any(os.scandir(dest)):
        return Err(DirectoryNotEmpty())


    repo: pg.Repository | None = None
    try:
        repo = pg.clone_repository(
            url=clone_args.repository_link, 
            path=clone_args.dest,
            bare=True,
            proxy=True,
            callbacks=AuthAgentCallback()
        )

    except pg.GitError as e:
        log.fatal("An error occured; error=%s", e)

        return Err(DirectoryNotEmpty())

    assert Path(repo.path).absolute() == dest.absolute(), "A BARE repository must be created at the designated path"

    return Ok(repo)
