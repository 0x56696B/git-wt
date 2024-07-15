use std::{collections::HashSet, path::PathBuf};

use git2::{Repository, Worktree};

use super::AddArgs;
use crate::helpers::{
  copy_funcs::copy_files,
  git::{
    config::{execute_config_cmds, get_wt_config},
    config_keys::{CONFIG_KEY_ADD_COMMANDS, CONFIG_KEY_EXCLUDE_FILES},
    ignored::get_files_for_cp,
    repo::{get_bare_git_repo, get_repo_name},
    worktrees::{create_new_worktree, get_default_worktree},
  },
};

/// Function to execute Command::Add
pub fn add_command(args: AddArgs) -> Result<(), String> {
  let bare_repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;
  let worktree: Worktree =
    create_new_worktree(&bare_repo, args.new_branch_name.as_str(), args.force)
      .map_err(|e| e.to_string())?;

  println!("New Worktree Created: {:?}; Repo: {:?}", worktree.path(), bare_repo.path());

  let excluded_files = get_excluded_files(&bare_repo)?;
  let main_branch_repo: Repository = get_default_worktree()?;

  let ignored_files: HashSet<PathBuf> =
    get_files_for_cp(&main_branch_repo, &args.exclude, &excluded_files)
      .map_err(|e| e.to_string())?;

  let root_src = main_branch_repo.workdir().ok_or("Unable to find workdir for default branch")?;
  let root_dest = &worktree.path();
  let file_paths = ignored_files.iter().map(|file| file.as_path()).collect();

  let _ = copy_files(root_src, root_dest, file_paths);

  let worktree_path = worktree.path().to_str().unwrap();
  let _ = execute_config_cmds(&bare_repo, worktree_path, CONFIG_KEY_ADD_COMMANDS)?;

  return Ok(());
}

fn get_excluded_files(repo: &Repository) -> Result<Vec<String>, String> {
  let config = get_wt_config()?;
  let repo_name = get_repo_name(&repo)?;

  let config_key: String = format!("{}.{}", repo_name, CONFIG_KEY_EXCLUDE_FILES);
  let excluded_files_entry = config.multivar(&config_key, None).map_err(|e| e.to_string())?;

  let mut entries = Vec::new();
  let _ = excluded_files_entry
    .for_each(|entry| {
      let value = entry.value().unwrap_or("").to_string();

      entries.push(value)
    })
    .map_err(|e| e.to_string())?;

  return Ok(entries);
}
