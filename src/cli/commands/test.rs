use git2::Repository;

use crate::helpers::git::repo::get_bare_git_repo;

use super::TestArgs;

pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let bare_repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;

  let worktree = bare_repo.find_worktree("feat-test").unwrap();

  println!("Found: {:?}", worktree.path());

  return Ok(());
}
