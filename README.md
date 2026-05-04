# git-wt

![License](https://img.shields.io/github/license/0x56696B/git-wt) ![Language](https://img.shields.io/github/languages/top/0x56696B/git-wt)

**git-wt** makes Git worktrees a first-class part of your workflow. Clone repos the right way, spin up isolated working environments per branch in seconds, and tear them down just as fast — without remembering a single plumbing command.

---

## Why worktrees?

The standard Git workflow — stash, switch branch, work, switch back, pop stash — gets painful fast. Worktrees let you check out multiple branches simultaneously, each in its own directory. No stashing. No context switching. Work on a hotfix in one terminal window while your feature branch stays untouched in another.

---

## Features

**Bare-repo cloning.** `git wt clone` sets up the correct repository structure automatically. No manual `git clone --bare` and no fiddling with `origin` HEAD refs.

**Ignored-file propagation.** When you create a new worktree, `git-wt` copies git-ignored files from the source branch — `.env`, `node_modules`, compiled outputs — so the new branch is immediately runnable. Control which patterns to skip via `--exclude` or the config file.

**Unmerged-commit protection.** `git wt rm` checks whether the branch has commits that haven't landed in the default branch yet. It won't delete anything until you confirm or pass `--force`.

**Per-repo lifecycle hooks.** Configure commands that run automatically after every `add` or `rm`:

```bash
git wt config --add-command "npm install" --add-command "cp .env.example .env"
git wt config --remove-command "docker compose down"
```

**Branch name sanitisation.** Branches like `feat/my-feature` are stored as `feat-my-feature` on disk, avoiding unintended subdirectory nesting.

---

## Command reference

| Command | Description |
|---------|-------------|
| `git wt clone <repo> <dir>` | Clone as a bare repo and create the default worktree. |
| `git wt add <branch> [from]` | Create a new worktree, optionally derived from a specific branch. |
| `git wt pull <branch>` | Fetch a remote branch and create a worktree for it. |
| `git wt rm <branch...>` | Remove one or more worktrees. Guards against unmerged work. |
| `git wt destroy <dir>` | Delete an entire bare repo and all its worktrees. |
| `git wt config [options]` | View or update per-repository settings. |

Run `git wt <command> --help` for the full options of any command.

---

## Workflow

```bash
# Clone and get to work immediately
git wt clone git@github.com:acme/my-app.git ~/projects/my-app
cd ~/projects/my-app/main

# New feature? Spin up a worktree — .env and node_modules already copied over
git wt add feat/auth main

# A colleague pushed a branch? Pull it as a worktree
git wt pull feat/payment-service

# Done with a branch? Remove it (merge check included)
git wt rm feat-auth
git wt rm feat-auth --force    # skip the merge check
git wt rm feat-a feat-b feat-c # remove several at once

# Project wrapped up? Tear the whole thing down
git wt destroy ~/projects/my-app
```

---

## Per-repo configuration

`git wt config` stores settings per repository in `~/.gitconfig_wt`. Set once, applied every time:

```bash
# Skip these when copying ignored files to a new worktree
git wt config -e "node_modules" -e "dist" -e ".turbo"

# Set the default branch for merge checks
git wt config --default-branch develop

# View current settings for this repo
git wt config --list
```

---

## Requirements

- Python ≥ 3.12
- An SSH agent with your key loaded (`ssh-add`) for `clone` and `pull`

---

## Installation

```bash
pipx install https://github.com/0x56696B/git-wt/archive/refs/tags/v1.0.1.tar.gz
```

Once installed, Git picks it up automatically:

```bash
git wt --help
```

---

## License

GPL-3.0 — see `LICENSE`.
