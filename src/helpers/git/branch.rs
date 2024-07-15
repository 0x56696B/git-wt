use std::{path::Path, process::Command};

use git2::{Branch, BranchType, Commit, Oid, Repository, Worktree};

// TODO: Pull from cache
pub(crate) fn get_repo_default_branch_name() -> Result<String, String> {
  let output = Command::new("git")
    .arg("ls-remote")
    .arg("--symref")
    //TODO: Make it dynamically get remote name (origin could be renamed to something else)
    .arg("origin")
    .arg("HEAD")
    .output()
    .map_err(|e| format!("Failed to execute git command: {}", e))?;

  if !output.status.success() {
    let stderr = String::from_utf8_lossy(&output.stderr);

    return Err(format!("Git command failed: {}", stderr));
  }

  let symref: String = String::from_utf8_lossy(&output.stdout).trim()[16..]
    .chars()
    .into_iter()
    .take_while(|&x| x != ' ' && x != '\t')
    .collect();

  let parsed = &symref[0..symref.len()];
  return Ok(String::from(parsed));
}

pub(crate) fn get_worktree_branch_name(worktree: &Worktree) -> Result<String, String> {
  let worktree_path: &Path = &worktree.path();

  return get_branch_name_from_path(worktree_path);
}

//NOTE: No way to get branch name from git2-rs, for now
pub(crate) fn get_branch_name_from_path(path: &Path) -> Result<String, String> {
  let output = Command::new("git")
    .arg("-C")
    .arg(path)
    .arg("rev-parse")
    .arg("--abbrev-ref")
    .arg("HEAD")
    .output()
    .map_err(|e| format!("Failed to execute git command: {}", e))?;

  if output.status.success() {
    let branch_name = String::from_utf8_lossy(&output.stdout).trim().to_string();

    Ok(branch_name)
  } else {
    let stderr = String::from_utf8_lossy(&output.stderr);

    Err(format!("Git command failed: {}", stderr))
  }
}

pub(crate) fn detect_worktree_merged(
  bare_repo: &Repository,
  worktree_branch_name: &str,
  main_branch_name: &str,
) -> Result<bool, String> {
  let main_branch: Branch = bare_repo
    .find_branch(main_branch_name, BranchType::Local)
    .map_err(|e| e.message().to_string())?;
  let main_commit: Commit =
    main_branch.get().peel_to_commit().map_err(|e| e.message().to_string())?;

  let worktree_branch = bare_repo
    .find_branch(worktree_branch_name, BranchType::Local)
    .map_err(|e| e.message().to_string())?;
  let worktree_commit =
    worktree_branch.get().peel_to_commit().map_err(|e| e.message().to_string())?;

  let merge_base: Oid = bare_repo
    .merge_base(main_commit.id(), worktree_commit.id())
    .map_err(|e| e.message().to_string())?;

  return Ok(merge_base == worktree_commit.id());
}
