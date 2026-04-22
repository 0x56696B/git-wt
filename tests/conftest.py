import pytest
import pygit2 as pg


@pytest.fixture
def local_origin(tmp_path):
    """
    Create a local bare git repository with an initial commit.

    Returns the string path to the bare repository, suitable for use as
    a repository_link in CloneArgs. Uses only local filesystem — no network,
    no SSH, no auth callbacks involved.
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

    # Step 3: clone source as a bare repo (becomes the fake origin)
    bare_path = tmp_path / "origin_bare"
    pg.clone_repository(str( source_path ), str( bare_path ), bare=True)

    return str( bare_path )
