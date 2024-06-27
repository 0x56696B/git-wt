pub mod ignored;

use git2::Repository;
use std::{env, path::PathBuf};

pub fn get_bare_git_repo() -> Result<Repository, String> {
  let current_dir: PathBuf = env::current_dir().map_err(|e| e.to_string())?;
  let repo = Repository::discover(current_dir).map_err(|e| e.message().to_string())?;

  if !repo.is_bare() {
    return Err("Not a bare git repository!".to_string());
  }

  return Ok(repo);
}

pub fn get_default_worktree() -> Result<Repository, String> {
  let mut current_dir: PathBuf = env::current_dir().map_err(|e| e.to_string())?;

  current_dir.push(get_repo_default_branch());

  return Repository::discover(current_dir).map_err(|e| e.message().to_string());
}

// TODO: Implement
fn get_repo_default_branch() -> String {
  return String::from("main");
}
