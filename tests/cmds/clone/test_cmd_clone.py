import pytest
import pygit2 as pg
from pathlib import Path
from result import Ok, Err

from src.cmds.clone.cmd_clone import clone_repository
from src.cmds.clone.args_clone import CloneArgs
from src.errors.path_cannot_be_file import PathCannotBeFile
from src.errors.directory_not_empty import DirectoryNotEmpty


class TestCloneRepository:

    def test_clone_success_creates_bare_repo(self, local_origin, tmp_path):
        """Happy path: cloned repo is bare and result is Ok."""
        dest = tmp_path / "target"
        clone_args = CloneArgs(repository_link=local_origin, dest=dest)

        result = clone_repository(clone_args)

        try:
            assert isinstance(result, Ok)
            repo: pg.Repository = result.ok_value
            assert dest.exists()
            assert repo.is_bare
        finally:
            # Explicitly release the pg.Repository handle so libgit2 drops
            # its file locks before _tmp_path_cleanup runs shutil.rmtree.
            # Without this, a test failure keeps `result` alive in pytest's
            # traceback frame, which can silently block directory removal.
            del result

    def test_clone_success_creates_default_worktree(self, local_origin, tmp_path):
        """After clone, the default worktree directory (main/) exists with a .git pointer."""
        dest = tmp_path / "target"
        clone_args = CloneArgs(repository_link=local_origin, dest=dest)

        result = clone_repository(clone_args)

        try:
            assert isinstance(result, Ok)
            worktree_path: Path = dest / "main"
            assert worktree_path.exists()
            assert worktree_path.is_dir()
            assert (worktree_path / ".git").exists()
        finally:
            # Explicitly release the pg.Repository inside result.ok_value.
            del result

    def test_clone_creates_directory_if_not_exists(self, local_origin, tmp_path):
        """Destination that does not exist gets created and clone succeeds."""
        dest = tmp_path / "new_dir" / "nested"
        assert not dest.exists()

        clone_args = CloneArgs(repository_link=local_origin, dest=dest)
        result = clone_repository(clone_args)

        try:
            assert isinstance(result, Ok)
            assert dest.exists()
            assert dest.is_dir()
        finally:
            # Explicitly release the pg.Repository inside result.ok_value.
            del result

    def test_clone_fails_if_dest_is_file(self, local_origin, tmp_path):
        """Destination is an existing file — must return Err(PathCannotBeFile())."""
        dest = tmp_path / "target_file"
        dest.write_text("I am a file")

        clone_args = CloneArgs(repository_link=local_origin, dest=dest)
        result = clone_repository(clone_args)

        assert isinstance(result, Err)
        assert isinstance(result.err_value, PathCannotBeFile)

    def test_clone_fails_if_dest_not_empty(self, local_origin, tmp_path):
        """Non-empty destination directory must return Err(DirectoryNotEmpty())."""
        dest = tmp_path / "target_nonempty"
        dest.mkdir()
        (dest / "existing.txt").write_text("content")

        clone_args = CloneArgs(repository_link=local_origin, dest=dest)
        result = clone_repository(clone_args)

        assert isinstance(result, Err)
        assert isinstance(result.err_value, DirectoryNotEmpty)
