use std::{collections::HashSet, path::PathBuf};

use git2::{Repository, Worktree};

use super::AddArgs;
use crate::helpers::{
  copy_funcs::copy_files,
  git::{
    ignored::get_ignored_files,
    repo::get_bare_git_repo,
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

  let main_branch_repo: Repository = get_default_worktree()?;
  let ignored_files: HashSet<PathBuf> =
    get_ignored_files(&main_branch_repo, &args.exclude).map_err(|e| e.to_string())?;

  let root_src = main_branch_repo.workdir().ok_or("Unable to find workdir for default branch")?;
  let root_dest = worktree.path();
  let file_paths = ignored_files.iter().map(|file| file.as_path()).collect();
  copy_files(root_src, root_dest, file_paths).map_err(|e| e)?;

  //TODO: Execute create config commands
  return Ok(());
}
