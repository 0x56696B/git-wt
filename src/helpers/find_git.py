from pathlib import Path


def get_git_dir(start: str) -> str | None:
    path = Path(start)
    git = path / ".git"

    # If git is a file, then we're in a branch of the worktree
    if git.is_file():
        return str( path.parent )

    # If git is a dir, then we're not in a bare repo
    if git.is_dir():
        return None

    # If at least 3 are present, then we're in the bare repo's root
    bare_root_dic = {
        'config': False,
        'HEAD': False,
        'packed-refs': False,
        'objects': False,
        'FETCH_HEAD': False
    }

    for dir in path.iterdir():
        if dir.name in bare_root_dic:
            bare_root_dic[dir.name] = True

    contains_git_files: bool = sum(bare_root_dic.values()) >= 3
    if contains_git_files:
        return str( path.absolute() )
    else:
        return None

