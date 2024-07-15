use git2::{Repository, Worktree};

use crate::helpers::git::repo::get_bare_git_repo;

use super::TestArgs;
pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let bare_repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;

  let worktree_name = "feat-test";
  let wts = bare_repo.worktrees().map_err(|e| e.message().to_string())?;
  for worktree in wts.iter() {
    println!("{}", worktree.unwrap());
  }

  let worktree: Worktree =
    bare_repo.find_worktree(&worktree_name).map_err(|e| e.message().to_string())?;
  println!("WT: {}", worktree.path().display());

  return Ok(());
}
