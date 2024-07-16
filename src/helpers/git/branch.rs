use std::{path::Path, process::Command};

use git2::{Branch, BranchType, Commit, Oid, Repository};

use super::{
  config::{add_config_entry, get_config_entry},
  config_keys::CONFIG_KEY_DEFAULT_BRANCH,
};

pub(crate) fn get_default_branch_name(repo_name: &str) -> Result<String, String> {
  let config_entry = get_config_entry(repo_name, CONFIG_KEY_DEFAULT_BRANCH);
  if config_entry.is_ok() {
    return Ok(config_entry.unwrap());
  }

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

  let _ = add_config_entry(repo_name, CONFIG_KEY_DEFAULT_BRANCH, parsed);

  return Ok(String::from(parsed));
}

pub(crate) fn get_wt_branch_name(wt_path: &Path) -> Result<String, String> {
  return Repository::open(wt_path)
    .map_err(|e| e.message().to_string())?
    .revparse_ext("HEAD")
    .map_err(|e| e.message().to_string())?
    .1
    .ok_or("No reference found for HEAD".to_string())?
    .shorthand()
    .map(|x| x.to_string())
    .ok_or("No shorthand for reference".to_string());
}

pub(crate) fn detect_wt_merged(
  repo: &Repository,
  wt_branch_name: &str,
  main_branch_name: &str,
) -> Result<bool, String> {
  let main_branch: Branch =
    repo.find_branch(main_branch_name, BranchType::Local).map_err(|e| e.message().to_string())?;

  let main_commit: Commit =
    main_branch.get().peel_to_commit().map_err(|e| e.message().to_string())?;

  let wt_branch =
    repo.find_branch(wt_branch_name, BranchType::Local).map_err(|e| e.message().to_string())?;

  let wt_commit = wt_branch.get().peel_to_commit().map_err(|e| e.message().to_string())?;

  let merge_base: Oid =
    repo.merge_base(main_commit.id(), wt_commit.id()).map_err(|e| e.message().to_string())?;

  return Ok(merge_base == wt_commit.id());
}
