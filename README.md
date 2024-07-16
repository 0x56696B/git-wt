# git-wt

A git extension to make git worktree easier to use and more intuitive

## Manual Installation

1. Clone the repository
2. Ensure you have `cargo` binary (install `cargo` from rust website)
3. Build project with `cargo build -r`
4. Run `cargo install --path .`
5. Source shell (`source ~/.zshrc` or `source ~/.bashrc`)

## Planned features:

[x] git wt - Forbid to execute in non-git repo

[x] git wt add - Create a worktree and copy over all hidden files (.env, for example)

[-] git wt rm - Remove a worktree and copy the difference in hidden files (optional, on by default)

[] git wt open - Provide a script, saved per repo in cache, that opens a worktree (new tmux + nvim, opens vscode in worktree, etc)

[x] git wt config - Provide a script, saved per repo in cache, that executes a script after `git wt add` or after `git wt rm`

[] git wt migrate - Possible migrate non-bare repo to bare (if possible)

[-] Caching for main branch and main worktree discovery

[x] A file that saves the config per repo

[x] In the config file, allow to exclude copying of certain git ignored files on `git wt add`

TODO: Add tracing (rust::tracing)
TODO: Add some kind of rollback mechanism when something fails (libgit2 transactions?)
TODO: Think of maybe using channels to async print stuff to stdout/stderr to avoid colored functions

