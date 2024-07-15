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

pub fn get_repo_name(repo: &Repository) -> Result<&str, String> {
  return repo
    .path()
    .file_name()
    .ok_or("Unable to parse repo name")?
    .to_str()
    .ok_or("".to_string());
}
