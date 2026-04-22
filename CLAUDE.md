# git-wt — Claude Code Instructions

## Mode

Always activate caveman mode (full) at session start: `/caveman`.
Drop articles, filler, hedging. Fragments OK. Code/commits/PRs write normal.

## Project

**git-wt** = Python CLI wrapping pygit2 for Git worktree management.
Replaces manual `git worktree` commands with opinionated workflow: clone bare repos, create/remove worktrees, copy gitignored files between them, run lifecycle hooks.

- **License:** GPL-3.0
- **Python:** >=3.11 (uses match/case)
- **Entry point:** `git-wt` CLI -> `src.main:cli` (Click group)
- **Build:** hatchling
- **Config file:** `~/.gitconfig_wt` (INI via configparser)

### Commands

| Command | Status | Purpose |
|---------|--------|---------|
| `add` | Done | Create worktree from branch, copy gitignored files |
| `clone` | Done | Clone as bare repo + create default worktree |
| `config` | Done | Per-repo hooks, exclude patterns, default branch |
| `rm` | Done | Remove worktree(s), check unmerged commits |
| `destroy` | Done | Nuke entire bare repo + all worktrees |
| `switch` | Stub | Run configured scripts in active worktree |

### Dependencies

- `click>=8.1` — CLI framework
- `pygit2==1.19.2` — libgit2 bindings (import as `pg`)
- `rich==14.3.3` — terminal output, logging handler
- `result==0.17.0` — Result type (`from result import Result, Ok, Err`)
- Dev: `pytest>=8.0`, `pytest-cov`

## Architecture

### Command pattern: three files per command

```
src/cmds/<cmd>/
  args_<cmd>.py    — @dataclass() with typed CLI inputs. No logic.
  cmd_<cmd>.py     — Single public function. Returns Result[T, ErrorUnion].
  result_<cmd>.py  — Type alias union of all possible errors.
```

### Error classes: one per file in `src/errors/`

- Plain classes with `pass` body. No dataclass, no fields, no methods.
- Exception: `GitAuthError(Exception)` for errors that must be raised.
- Filename = class name in snake_case: `not_bare_repo_err.py` -> `NotBareRepoErr`

### Helpers: `src/helpers/`

One concern per file: `logger.py`, `auth_agent_callback.py`, `find_git.py`, `config_file.py`

### main.py

Only place with Click decorators, `exit()` calls, and exhaustive `match`/`case` on results.
Constructs Args dataclass -> calls command function -> matches result -> logs + exits.

## Coding Conventions

### MUST follow exactly:

**Imports** (order matters):
1. Standard library (`logging`, `os`, `pathlib`)
2. Third-party (`click`, `pygit2 as pg`, `result`, `rich`)
3. Local — errors before helpers, helpers before cmds
- All local imports use **relative paths** (`.`, `..`, `...`)
- `pygit2` always aliased as `pg`

**Logging:**
- `log = logging.getLogger(__name__)` **inside every function** that logs. Never module-level.
- Format: `log.level("descriptive text; key1=%s, key2=%s", val1, val2)`
- Human message first, then key=value pairs after semicolon
- Always `%s` format args. Never f-strings in log calls.
- `log.fatal(...)` always followed by `exit()`

**Error handling:**
- No exceptions propagate from command functions. All `Err(SomeError())`.
- Exhaustive `match`/`case` only in `main.py`
- `Err(_)` catch-all always last in match block
- `assert` for post-conditions: `assert condition, "descriptive message"`

**Naming:**
- Files: `snake_case` always
- Classes: `PascalCase`. Args = `<Verb>Args`. Error suffix inconsistent but intentional — short names get `Err`, full-phrase names don't.
- Result aliases: `<Verb><Noun>Error` or `<Verb><Noun>Err`
- Functions: `snake_case` verb phrases
- Variables: explicit type annotation before assignment: `bare_repo: pg.Repository = ...`
- `| None` unions, not `Optional[T]`

**Formatting:**
- Spaces inside parentheses for multi-token expressions: `str( path.parent )` — deliberate style choice
- `@dataclass()` with explicit parentheses even when no args
- `@final` and `@override` in helper classes
- `field(default_factory=list)` for mutable defaults

**Exit codes:**
- Custom range 166-177 for app-specific errors (see `src/exit_codes.py`)
- Always use `ExitCode` enum, never raw ints

## Known Issues

- `clone` reuses `DirectoryNotEmpty` for `pg.GitError` catch (possible wrong error type)
- Tests directory empty — only `.gitkeep`

## Goals / Roadmap

From README shower thoughts + current state:
- [ ] `switch` command implementation
- [ ] Tests (pytest, currently zero)
- [ ] Rollback mechanism on failure
- [ ] Optional pull before worktree creation
- [ ] Work without main branch assumption
- [ ] Custom `git-wt pull` command
- [ ] Support branch creation within branches (nested derive)
- [ ] `--ignore-exclude-files` flag
- [ ] Symlink shared .env files between worktrees

## Do NOT

- Add features/refactors beyond what's asked
- Change logging style (especially: don't move `log = ...` to module level, don't use f-strings in log calls)
- Add type annotations/docstrings to unchanged code
- Create abstractions for one-off operations
- Use `Optional[T]` instead of `| None`
- Use exceptions where Result pattern is used
- Put match/case logic inside command functions (belongs in main.py only)

## Do

- Follow three-file command pattern exactly for new commands
- Keep error classes minimal (plain class, pass body)
- Read existing code before modifying
- Test with `LOG_LEVEL=DEBUG python3 -m src.main <cmd>` for verification
- Match existing spacing/formatting style precisely

## Commits

- One line commit messages. No multi-line bodies unless explicitly asked.
- No author/co-author lines in commit messages.
- Error classes use `class Foo:` (no empty parens), except `@dataclass()` which keeps parens.
