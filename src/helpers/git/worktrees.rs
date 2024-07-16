use std::{env, path::PathBuf, process::Command};

use git2::{Repository, Worktree};

use super::{branch::get_default_branch_name, general::escape_branch_name};

//TODO: Pull from cache
pub fn get_default_worktree(repo_name: &str) -> Result<Repository, String> {
  let mut current_dir: PathBuf = env::current_dir().map_err(|e| e.to_string())?;
  let default_branch_name: String = get_default_branch_name(repo_name)?;

  current_dir.push(default_branch_name);

  return Repository::discover(current_dir).map_err(|e| e.message().to_string());
}

pub(crate) fn create_new_worktree(
  bare_repo: &Repository,
  branch_name: &str,
  force: bool,
) -> Result<Worktree, String> {
  let escaped_branch_name: String = escape_branch_name(branch_name);

  let mut cmd = Command::new("git");
  cmd
    .arg("worktree")
    .arg("add")
    .arg("--checkout")
    .arg("-B")
    .arg(&branch_name)
    .arg(&escaped_branch_name);

  if force {
    cmd.arg("--force");
  }

  let output = cmd.output().expect("Failed to execute create worktree command");
  if !output.status.success() {
    return Err(format!(
      "Unable to create worktree with branch {} at path {}",
      &branch_name, &escaped_branch_name
    ));
  }

  let worktree: Worktree =
    bare_repo.find_worktree(&escaped_branch_name).map_err(|e| e.message().to_string())?;

  return Ok(worktree);
}

pub(crate) fn remove_worktree(wt_name: &str, force: bool) -> Result<(), String> {
  // NOTE: Remove still doesn't exist in the git2-rs lib
  let mut cmd = Command::new("git");
  cmd.arg("worktree").arg("remove").arg(&wt_name);

  if force {
    cmd.arg("--force");
  }

  let output = cmd.output().expect("Failed to execute remove worktree command");
  if !output.status.success() {
    return Err(format!("Unable to remove worktree at path {}", &wt_name));
  }

  return Ok(());
}

pub(crate) fn prune_worktree(_wt: &Worktree, _force: bool) -> Result<(), String> {
  // let mut prune_options = WorktreePruneOptions::new();
  // prune_options.working_tree(true);
  //
  // let prunable = worktree.is_prunable(Some(&mut prune_options)).unwrap_or_else(|_| false);
  // if !prunable || !force {
  //   return Err(format!("Worktree {} is not prunable. Use --force to override", worktree_name));
  // }
  //
  // worktree.prune(Some(&mut prune_options));
  //
  return Ok(());
}

pub(crate) fn get_worktree(repo: &Repository, worktree_name: &str) -> Result<Worktree, String> {
  let contains_wt = repo
    .worktrees()
    .map_err(|e| e.message().to_string())?
    .iter()
    .filter_map(|wt| wt)
    .collect::<Vec<&str>>()
    .contains(&worktree_name);

  if !contains_wt {
    return Err("Worktree not contained in repo".to_string());
  }

  return repo.find_worktree(&worktree_name).map_err(|e| e.message().to_string());
}
