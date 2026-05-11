from pathlib import Path

import pygit2 as pg
from result import Err, Ok

from src.cmds.list.args_list import ListArgs
from src.cmds.list.cmd_list import list_worktrees
from src.errors.not_bare_repo_err import NotBareRepoErr


def _make_bare_repo(path: Path) -> pg.Repository:
    repo = pg.init_repository(str(path), bare=True)
    sig = pg.Signature("Test", "test@test.com")
    tree_id = repo.TreeBuilder().write()
    repo.create_commit("refs/heads/main", sig, sig, "Initial commit", tree_id, [])
    repo.set_head("refs/heads/main")
    return repo


def _add_branch(repo: pg.Repository, branch_name: str, wt_path: Path) -> pg.Worktree:
    main_commit: pg.Commit = repo.lookup_reference("refs/heads/main").peel(pg.Commit)
    branch_ref: pg.Reference = repo.create_reference(f"refs/heads/{branch_name}", main_commit.id, False)
    return repo.add_worktree(branch_name, str(wt_path), branch_ref)


class TestListWorktreesNotBareRepo:
    def test_non_bare_repo_returns_err(self, tmp_path: Path) -> None:
        non_bare = tmp_path / "not-bare"
        non_bare.mkdir()
        pg.init_repository(str(non_bare), bare=False)

        args = ListArgs(current_working_dir=str(non_bare), )
        result = list_worktrees(args)

        assert isinstance(result, Err)
        assert isinstance(result.err(), NotBareRepoErr)

    def test_plain_directory_returns_err(self, tmp_path: Path) -> None:
        args = ListArgs(current_working_dir=str(tmp_path), )
        result = list_worktrees(args)

        assert isinstance(result, Err)
        assert isinstance(result.err(), NotBareRepoErr)


class TestListWorktreesEmpty:
    def test_bare_repo_with_no_worktrees_returns_empty_list(self, tmp_path: Path) -> None:
        bare = tmp_path / "bare"
        bare.mkdir()
        _make_bare_repo(bare)

        args = ListArgs(current_working_dir=str(bare))
        result = list_worktrees(args)

        assert isinstance(result, Ok)
        assert result.ok() == []


class TestListWorktreesSingle:
    def test_single_worktree_name_and_path(self, tmp_path: Path) -> None:
        bare = tmp_path / "bare"
        bare.mkdir()
        repo = _make_bare_repo(bare)

        wt_path = tmp_path / "feat-x"
        _add_branch(repo, "feat-x", wt_path)

        args = ListArgs(current_working_dir=str(bare))
        result = list_worktrees(args)

        assert isinstance(result, Ok)
        worktrees = result.ok()
        assert len(worktrees) == 1
        assert worktrees[0].name == "feat-x"
        assert worktrees[0].path.rstrip("/") == str(wt_path)

    def test_worktree_not_prunable_when_path_exists(self, tmp_path: Path) -> None:
        bare = tmp_path / "bare"
        bare.mkdir()
        repo = _make_bare_repo(bare)
        _add_branch(repo, "feat-x", tmp_path / "feat-x")

        args = ListArgs(current_working_dir=str(bare))
        result = list_worktrees(args)

        assert isinstance(result, Ok)
        assert result.ok()[0].is_prunable is False


class TestListWorktreesMultiple:
    def test_multiple_worktrees_all_listed(self, tmp_path: Path) -> None:
        bare = tmp_path / "bare"
        bare.mkdir()
        repo = _make_bare_repo(bare)

        _add_branch(repo, "feat-a", tmp_path / "feat-a")
        _add_branch(repo, "feat-b", tmp_path / "feat-b")
        _add_branch(repo, "feat-c", tmp_path / "feat-c")

        args = ListArgs(current_working_dir=str(bare))
        result = list_worktrees(args)

        assert isinstance(result, Ok)
        names = {wt.name for wt in result.ok()}
        assert names == {"feat-a", "feat-b", "feat-c"}


class TestListWorktreesUnmerged:
    def test_worktree_on_same_commit_as_main_has_no_unmerged(self, tmp_path: Path) -> None:
        bare = tmp_path / "bare"
        bare.mkdir()
        repo = _make_bare_repo(bare)
        _add_branch(repo, "my-branch", tmp_path / "my-branch")

        args = ListArgs(current_working_dir=str(bare))
        result = list_worktrees(args)

        assert isinstance(result, Ok)
        assert result.ok()[0].has_unmerged_commits is False

    def test_worktree_with_extra_commit_has_unmerged(self, tmp_path: Path) -> None:
        bare = tmp_path / "bare"
        bare.mkdir()
        repo = _make_bare_repo(bare)
        _add_branch(repo, "feat-x", tmp_path / "feat-x")

        sig = pg.Signature("Test", "test@test.com")
        blob_id = repo.create_blob(b"extra")
        tb = repo.TreeBuilder()
        tb.insert("extra.txt", blob_id, pg.GIT_FILEMODE_BLOB)
        tree_id = tb.write()
        parent: pg.Commit = repo.lookup_reference("refs/heads/feat-x").peel(pg.Commit)
        repo.create_commit("refs/heads/feat-x", sig, sig, "extra commit", tree_id, [parent.id])

        args = ListArgs(current_working_dir=str(bare))
        result = list_worktrees(args)

        assert isinstance(result, Ok)
        assert result.ok()[0].has_unmerged_commits is True
