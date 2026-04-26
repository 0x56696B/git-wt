import gc
import shutil

import pygit2 as pg
import pytest


@pytest.fixture
def local_origin(tmp_path):
    """
    Create a local bare git repository with an initial commit.

    Returns the string path to the bare repository, suitable for use as
    a repository_link in CloneArgs. Uses only local filesystem — no network,
    no SSH, no auth callbacks involved.

    Teardown releases the pygit2 handles opened here so libgit2 drops any
    index/pack locks before the per-test tmp_path is wiped by the autouse
    cleanup fixture below.
    """
    # Step 1: init a non-bare source repo
    source_path = tmp_path / "origin_source"
    source_repo: pg.Repository = pg.init_repository(str( source_path ), bare=False)

    # Step 2: write a file, stage it, commit
    readme = source_path / "README.md"
    readme.write_text("# Test Repository\n")

    source_repo.index.read()
    source_repo.index.add("README.md")
    source_repo.index.write()

    tree = source_repo.index.write_tree()
    sig: pg.Signature = pg.Signature("Test Author", "test@test.com")

    source_repo.create_commit(
        "refs/heads/main",
        sig,
        sig,
        "initial commit",
        tree,
        []
    )

    # Point HEAD at main so the bare clone inherits the correct default branch.
    # pg.init_repository defaults HEAD to refs/heads/master; without this the
    # clone copies that broken symbolic ref and dest ends up with no
    # refs/heads/main — causing KeyError in lookup_reference.
    source_repo.set_head("refs/heads/main")

    # Step 3: clone source as a bare repo (becomes the fake origin)
    bare_path = tmp_path / "origin_bare"
    bare_repo = pg.clone_repository(str( source_path ), str( bare_path ), bare=True)

    try:
        yield str( bare_path )
    finally:
        # Drop pygit2 handles so libgit2 releases file locks before rmtree.
        del bare_repo
        del source_repo


@pytest.fixture(autouse=True)
def _tmp_path_cleanup(tmp_path):
    """
    Autouse teardown: wipe each test's tmp_path after the test finishes.

    pytest's default tmp_path retention keeps the three most recent sessions
    on disk. For this suite every test creates a fake origin + a bare clone
    + a default worktree, so that retention accumulates megabytes of stale
    repository state fast. Removing tmp_path explicitly keeps every test
    hermetic and prevents /tmp from ballooning across runs.

    gc.collect() runs first so any pygit2.Repository lingering in test scope
    is freed before libgit2's file handles would block the directory removal.
    """
    yield
    gc.collect()
    shutil.rmtree(tmp_path, ignore_errors=True)
