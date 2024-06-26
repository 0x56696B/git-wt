mod ignored;

use git2::Repository;
use std::{env, path::PathBuf};

pub fn get_bare_git_repo() -> Result<Repository, String> {
  let current_dir: PathBuf = match env::current_dir() {
    Ok(path) => path,
    Err(e) => return Err(e.to_string()),
  };

  let repo = match Repository::discover(current_dir) {
    Ok(repo) => repo,
    Err(e) => return Err(e.message().to_string()),
  };

  if !repo.is_bare() {
    return Err("Not a bare git repository!".to_string());
  }

  return Ok(repo);
}
