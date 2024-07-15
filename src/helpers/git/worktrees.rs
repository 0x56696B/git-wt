use std::{
  env,
  path::{Path, PathBuf},
  process::Command,
};

use git2::{Repository, Worktree, WorktreeAddOptions};

use super::{
  branch::{detect_worktree_merged, get_repo_default_branch_name, get_worktree_branch_name},
  general::{escape_branch_name, join_path},
};

//TODO: Pull from cache
pub fn get_default_worktree() -> Result<Repository, String> {
  let mut current_dir: PathBuf = env::current_dir().map_err(|e| e.to_string())?;
  let default_branch_name: String = get_repo_default_branch_name()?;

  current_dir.push(default_branch_name);

  return Repository::discover(current_dir).map_err(|e| e.message().to_string());
}

pub fn get_worktree_path(worktree: &Worktree) -> &Path {
  return worktree.path();
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

// FIXME: This doesn't work, for some reason. Doesn't map to branch and directory name properly
// Or I might be doing something wrong, idk
#[allow(dead_code)]
pub(crate) fn create_new_worktree_native(
  bare_repo: &Repository,
  branch_name: &str,
  force: bool,
) -> Result<Worktree, String> {
  let repo_path: &Path = bare_repo.path();
  let escaped_branch_name: String = escape_branch_name(branch_name);
  let new_worktree_path: PathBuf = join_path(repo_path, &escaped_branch_name);

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

// FIXME: Fix, not working find_worktree
pub(crate) fn remove_worktree(
  repo: &Repository,
  worktree_name: &str,
  force: bool,
) -> Result<(), String> {
  let worktree: Worktree = get_worktree(repo, worktree_name)?;

  let worktree_branch_name = get_worktree_branch_name(&worktree).map_err(|e| e.to_string())?;
  let default_branch_name: String = get_repo_default_branch_name()?;

  // let mut prune_options = WorktreePruneOptions::new();
  // prune_options.working_tree(true);

  if !force {
    let merged =
      detect_worktree_merged(repo, &worktree_branch_name, &default_branch_name).map_err(|e| e)?;

    if !merged {
      return Err(format!("Worktree {0} has not been merged to {1} branch. Use --force to override or merge it with {1}", worktree_name, default_branch_name));
    }

    // let prunable = worktree.is_prunable(Some(&mut prune_options)).unwrap_or_else(|_| false);
    // if !prunable {
    //   return Err(format!("Worktree {} is not prunable. Use --force to override", worktree_name));
    // }
  }

  // NOTE: Remove still doesn't exist in the git2-rs lib
  let mut cmd = Command::new("git");
  cmd.arg("worktree").arg("remove").arg(&worktree_name);

  if force {
    cmd.arg("--force");
  }

  let output = cmd.output().expect("Failed to execute remove worktree command");
  if !output.status.success() {
    return Err(format!("Unable to remove worktree at path {}", &worktree_name));
  }

  // worktree.prune(Some(&mut prune_options));

  return Ok(());
}

fn get_worktree(repo: &Repository, worktree_name: &str) -> Result<Worktree, String> {
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
