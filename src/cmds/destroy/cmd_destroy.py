import logging
import shutil
from pathlib import Path

import pygit2 as pg
from result import Err, Ok, Result

from .args_destroy import DestroyArgs
from .result_destroy import DestroyRepoError
from ...errors.destroy_err import DestroyErr
from ...errors.directory_not_found_err import DirectoryNotFoundErr
from ...errors.not_bare_repo_err import NotBareRepoErr
from ...helpers.config_file import remove_repo_entry


def destroy_repo(destroy_args: DestroyArgs) -> Result[None, DestroyRepoError]:
    log = logging.getLogger(__name__)

    directory: Path = Path(destroy_args.directory).absolute()

    log.debug(
        "Attempting to destroy bare repo; directory=%s, force=%s",
        directory,
        destroy_args.force,
    )

    if not directory.exists():
        log.warning("Directory does not exist; directory=%s", directory)
        return Err(DirectoryNotFoundErr())

    try:
        bare_repo: pg.Repository = pg.Repository(
            str(directory), flags=pg.enums.RepositoryOpenFlag.BARE
        )
    except pg.GitError:
        log.warning("Not a valid bare git repository; directory=%s", directory)
        return Err(NotBareRepoErr())

    if not bare_repo.is_bare:
        log.warning("Not a bare git repository; directory=%s", directory)
        return Err(NotBareRepoErr())

    log.debug("Bare repository confirmed; directory=%s", directory)

    log.debug("Removing directory tree; directory=%s", directory)

    try:
        shutil.rmtree(str(directory))
    except OSError as e:
        log.error("Failed to remove directory; directory=%s, error=%s", directory, e)
        return Err(DestroyErr())

    log.info("Directory removed; directory=%s", directory)

    config_res = remove_repo_entry(str(directory))
    match config_res:
        case Err(_) as err:
            return err
        case Ok(_):
            pass

    log.info("Bare repository destroyed successfully; directory=%s", directory)

    return Ok(None)
