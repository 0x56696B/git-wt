import logging
from typing import final, override

from pygit2 import CredentialType, KeypairFromAgent, RemoteCallbacks
from pygit2.remotes import TransferProgress
from rich.progress import Progress

from ..errors.git_auth_error import GitAuthError


@final
class AuthAgentCallback(RemoteCallbacks):
    def __init__(self):
        super().__init__()
        self._progress = Progress(transient=True, auto_refresh=False)
        self._task = None

    @override
    def credentials(self, url, username_from_url, allowed_types):
        log = logging.getLogger(__name__)
        if allowed_types & CredentialType.SSH_KEY:
            log.debug("Using SSH agent for credentials; url=%s, username=%s", url, username_from_url)
            return KeypairFromAgent(username_from_url)

        log.error("No supported credential type available; url=%s, allowed_types=%s", url, allowed_types)
        raise GitAuthError()

    @override
    def transfer_progress(self, stats: TransferProgress):
        if stats.total_objects == 0:
            return

        if not self._progress.live.is_started:
            self._progress.start()

        if stats.received_objects == stats.total_objects:
            self._progress.stop()
            return

        if self._task is None:
            self._task = self._progress.add_task(description="", total=stats.total_objects, completed=stats.indexed_objects)

        self._progress.update(self._task, description=None, completed=stats.indexed_objects, refresh=True)
