use crate::helpers::git::{repo::get_bare_git_repo, worktrees::get_worktree};

use super::TestArgs;

pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let repo = get_bare_git_repo()?;
  let wt_name = "feat-PZ-513-jwt-cognito-service";

  let wt = get_worktree(&repo, &wt_name)?;
  println!("Name: {:?}", wt.name());
  println!("Path: {:?}", wt.path());
  println!("valid: {:?}", wt.validate());
  return Ok(());
}
