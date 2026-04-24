from enum import IntEnum


class ExitCode(IntEnum):
    # Standard
    SUCCESS = 0
    ERR_GENERAL = 1
    ERR_MISUSE = 2  # Misuse of shell built-ins / bad arguments
    ERR_NO_EXEC = 126  # Command found but not executable
    ERR_NOT_FOUND = 127  # Command not found

    # App-specific (166–254 range reserved for custom use)
    ERR_PATH_IS_FILE = 166  # Destination path is a file, expected directory
    ERR_DIR_NOT_EMPTY = 167  # Destination directory is not empty
    ERR_NOT_BARE_REPO = 168  # No bare git repository found
    ERR_WORKTREE = 169  # Worktree creation failed
    ERR_BRANCH_MISSING = 170  # Derived branch does not exist
    ERR_NO_FF_MERGE = 171  # Branch requires true merge, cannot fast-forward
    ERR_CONFIG_READ = 172  # Failed to read config file
    ERR_CONFIG_WRITE = 173  # Failed to write config file
    ERR_CONFIG_PERM = 174  # Insufficient permissions on config file
    ERR_UNMERGED = 175  # Branch has commits not present in default branch
    ERR_WORKTREE_MISSING = 176  # Worktree or branch not found
    ERR_DIR_NOT_FOUND = 177  # Directory does not exist
