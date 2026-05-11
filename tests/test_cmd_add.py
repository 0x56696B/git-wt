import os
from pathlib import Path

import pygit2 as pg
import pytest
from result import Err, Ok

from src.cmds.add.args_add import AddArgs
from src.cmds.add.cmd_add import add_worktree
from src.errors.not_bare_repo_err import NotBareRepoErr


def _make_bare_repo_with_main_worktree(tmp_path: Path) -> tuple[pg.Repository, Path]:
    bare = tmp_path / "bare"
    bare.mkdir()
    repo = pg.init_repository(str(bare), bare=True)

    sig = pg.Signature("Test", "test@test.com")
    tree_id = repo.TreeBuilder().write()
    repo.create_commit("refs/heads/main", sig, sig, "Initial commit", tree_id, [])
    repo.set_head("refs/heads/main")

    main_path = bare / "main"
    branch_ref: pg.Reference = repo.lookup_reference("refs/heads/main")
    repo.add_worktree("main", str(main_path), branch_ref)

    return repo, bare


class TestAddWorktreeNotBareRepo:
    def test_plain_directory_returns_err(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(str(tmp_path))

        args = AddArgs(
            new_branch_name="feat-x",
            derive_from_branch="main",
            should_nest_dirs=False,
            exclude=[],
            _force=False,
        )
        result = add_worktree(args)

        assert isinstance(result, Err)
        assert isinstance(result.err(), NotBareRepoErr)


class TestAddWorktreeUpToDate:
    def test_up_to_date_base_creates_worktree(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        repo, bare = _make_bare_repo_with_main_worktree(tmp_path)
        monkeypatch.chdir(str(bare))

        args = AddArgs(
            new_branch_name="feat-x",
            derive_from_branch="main",
            should_nest_dirs=False,
            exclude=[],
            _force=False,
        )
        result = add_worktree(args)

        assert isinstance(result, Ok)
        assert (bare / "feat-x").exists()


class TestAddWorktreeFastForward:
    def test_fast_forward_base_does_not_crash(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        repo, bare = _make_bare_repo_with_main_worktree(tmp_path)

        # Add a second commit to main so it is ahead of HEAD
        sig = pg.Signature("Test", "test@test.com")
        blob_id = repo.create_blob(b"content")
        tb = repo.TreeBuilder()
        tb.insert("file.txt", blob_id, pg.GIT_FILEMODE_BLOB)
        tree_b = tb.write()
        parent: pg.Commit = repo.lookup_reference("refs/heads/main").peel(pg.Commit)
        repo.create_commit("refs/heads/main", sig, sig, "second commit", tree_b, [parent.id])

        # Detach HEAD at the first commit so main is one ahead (FASTFORWARD scenario)
        # pygit2 1.19.2 has no set_head_detached; write the HEAD file directly
        with open(os.path.join(str(bare), "HEAD"), "w") as f:
            f.write(str(parent.id) + "\n")

        # Capture target OID (tip of main after second commit) before calling add_worktree
        target_oid: pg.Oid = repo.lookup_reference("refs/heads/main").peel(pg.Commit).id

        monkeypatch.chdir(str(bare))

        args = AddArgs(
            new_branch_name="feat-y",
            derive_from_branch="main",
            should_nest_dirs=False,
            exclude=[],
            _force=False,
        )
        result = add_worktree(args)

        # Must succeed — old code raised GitError from checkout_tree on bare repo
        assert isinstance(result, Ok)
        assert (bare / "feat-y").exists()
        # Verify FASTFORWARD branch was taken: refs/heads/main must point at target_oid
        assert repo.lookup_reference("refs/heads/main").peel(pg.Commit).id == target_oid
