from pathlib import Path


def get_git_dir(start: str) -> str | None:
    path = Path(start)
    git = path / ".git"

    # If git is a file, then we're in a branch of the worktree
    if git.is_file():
        return str( path.parent )

    # If git is a dir, then we're not in a bare repo
    elif git.is_dir():
        return None

    # If all of them are true, then we're in the bare repo's root
    bare_root_dic = {
        'config': False,
        'HEAD': False,
        'packed-refs': False,
        'objects': False
    }

    for dir in path.iterdir():
        if dir.name in bare_root_dic:
            bare_root_dic[dir.name] = True

    contains_git_files: bool = all(dic_values for dic_values in bare_root_dic.values())
    if contains_git_files:
        return str( path.absolute() )
    else:
        return None

