use std::{
  env,
  path::{Path, PathBuf},
};

use git2::{Repository, Worktree, WorktreeAddOptions};

use super::{
  branch::get_repo_default_branch,
  general::{escape_branch_name, join_path},
};

//TODO: Pull from cache
pub fn get_default_worktree() -> Result<Repository, String> {
  let mut current_dir: PathBuf = env::current_dir().map_err(|e| e.to_string())?;

  current_dir.push(get_repo_default_branch());

  return Repository::discover(current_dir).map_err(|e| e.message().to_string());
}

pub(crate) fn create_new_worktree(
  bare_repo: &Repository,
  branch_name: &str,
  force: bool,
) -> Result<Worktree, String> {
  let repo_path: &Path = bare_repo.path();
  let escaped_branch_name: String = escape_branch_name(branch_name);
  let new_worktree_path: PathBuf = join_path(repo_path, escaped_branch_name.as_str());

  let mut add_options = WorktreeAddOptions::new();
  if force {
    add_options.checkout_existing(true);
  }

  return match bare_repo.worktree(
    &escaped_branch_name,
    new_worktree_path.as_path(),
    Some(&add_options),
  ) {
    Ok(worktree) => Ok(worktree),
    Err(e) => Err(e.message().to_string()),
  };
}
