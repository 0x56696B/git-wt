# git-wt

![License](https://img.shields.io/github/license/0x56696B/git-wt) ![Language](https://img.shields.io/github/languages/top/0x56696B/git-wt)

**git-wt** is a Git extension designed to simplify the management of Git worktrees, making them easier and more intuitive to use.

## Features

- **Simplified Worktree Management:** Easily create, remove, and automate worktrees with custom scripts.
- **Flexible Commands:** Supports `add`, `rm`, and `open` commands tailored for worktree directory management.
- **Configuration and Caching:** Allows per-repository configuration and caching for more efficient workflows.

## Installation

To install `git-wt`, clone the repository and build it using Cargo:

```bash
git clone https://github.com/0x56696B/git-wt.git
cd git-wt
cargo build --release
cargo install --path .
```

## Usage

The main commands available with git-wt include:

```bash
git wt add <worktree-name>     # Adds a new worktree
git wt rm <worktree-name>      # Removes an existing worktree
git wt open <worktree-name>    # Opens a specified worktree
```

Additional Options:
Run `git wt --help`` for a full list of commands and options.
Run `git wt <command> --help` for more information regarding a particular command

## Planned features

[x] git wt - Forbid to execute in non-git repo

[x] git wt add - Create a worktree and copy over all hidden files (.env, for example)

[-] git wt rm - Remove a worktree and copy the difference in hidden files (optional, on by default)

[] git wt open - Provide a script, saved per repo in cache, that opens a worktree (new tmux + nvim, opens vscode in worktree, etc)

[x] git wt config - Provide a script, saved per repo in cache, that executes a script after `git wt add` or after `git wt rm`

[] git wt migrate - Possible migrate non-bare repo to bare (if possible)

[-] Caching for main branch and main worktree discovery

[x] A file that saves the config per repo

[x] In the config file, allow to exclude copying of certain git ignored files on `git wt add`

## Shower Thoughts
TODO: Add tracing (rust::tracing)
TODO: Add some kind of rollback mechanism when something fails (libgit2 transactions?)
TODO: Think of maybe using channels to async print stuff to stdout/stderr to avoid colored functions
TODO: Optionally pull main before creation of new worktree
TODO: Make work without main branch present (first time repo)
TODO: Create git-wt pull to pull as bare repo properly
TODO: Make so creation can take place in a branch, but still recognize the bare repo folder (ex: from some-branch branch to be able to create a new one, without showing the "not a bare repo" error)
TODO: Add flag to ignore excluded files in `git-wt add`

FIX: `git wt config -e "node_modules" "cache"` doesn't work, but `git wt config -e "node_modules" -e "cache"` works

TODO: Make `git-wt switch` to run a script in the active worktree (ex: `main` wt runs `docker compose up`, but I can't do the same in another wt, until I `docker compose down` in `main`)

## License
This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## Contact
Feel free to open an issue for any bug reports or feature requests. Your feedback is valuable!

