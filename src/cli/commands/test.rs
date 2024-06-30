use git2::Repository;

use crate::helpers::git::{branch::get_repo_default_branch_name, repo::get_bare_git_repo};

use super::TestArgs;

pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let _bare_repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;

  let branch_name: String = get_repo_default_branch_name().unwrap();
  for c in branch_name.chars() {
    println!("C: {} is {}", c, c as u8);
  }

  return Ok(());
}
