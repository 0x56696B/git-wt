use std::{env, path::PathBuf};

use git2::Repository;

pub fn get_bare_git_repo() -> Result<Repository, String> {
  let current_dir: PathBuf = env::current_dir().map_err(|e| e.to_string())?;
  let repo: Repository = Repository::discover(current_dir).map_err(|e| e.message().to_string())?;

  if !repo.is_bare() {
    return Err("Not a bare git repository!".to_string());
  }

  return Ok(repo);
}
