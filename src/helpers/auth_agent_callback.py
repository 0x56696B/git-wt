import logging
from typing import final, override
from pygit2 import CredentialType, KeypairFromAgent, RemoteCallbacks
from pygit2.remotes import TransferProgress
from rich.progress import Progress

from ..errors.git_auth_error import GitAuthError

from .logger import console

@final
class AuthAgentCallback(RemoteCallbacks):
    def __init__(self):
        super().__init__()

        self._progress = Progress(
            redirect_stderr=True,
            redirect_stdout=True,
            console=console,  # same console as RichHandler
        )

        _ = self._task = None
        _ = self._progress.__enter__()

    @override
    def credentials(self, url: str, username_from_url: str | None, allowed_types: CredentialType):
        if allowed_types & CredentialType.SSH_KEY:
            return KeypairFromAgent(username_from_url or "git")

        raise GitAuthError(f"Unsupported credential type: {allowed_types}")

    @override
    def transfer_progress(self, stats: TransferProgress):
        log = logging.getLogger(__name__)

        if stats.total_objects == 0:
            return

        if stats.total_objects == stats.indexed_objects:
            log.debug("Downloading finished; total_objects=%s, processed_objects=%s", stats.total_objects, stats.indexed_objects)

            self._progress.__exit__(None, None, None)
            return

        if self._task is None:
            self._task = self._progress.add_task(
                description="",
                total=stats.total_objects,
                completed=stats.indexed_objects
            )

        self._progress.update(
            self._task,
            description=None,
            completed=stats.indexed_objects,
            refresh=True
        )
