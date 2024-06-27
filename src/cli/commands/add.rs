use std::path::{Path, PathBuf};

use git2::{Repository, Worktree, WorktreeAddOptions};

use super::AddArgs;
use crate::helpers::git::{get_bare_git_repo, get_default_worktree, ignored::get_ignored_files};

/// Function to execute Command::Add
pub fn add_command(args: AddArgs) -> Result<(), String> {
  let bare_repo = get_bare_git_repo().map_err(|e| e.to_string())?;
  let worktree: Worktree =
    create_new_worktree(&bare_repo, args.new_branch_name.as_str()).map_err(|e| e.to_string())?;

  println!("New Worktree Created: {:?}; Repo: {:?}", worktree.path(), bare_repo.path());

  let main_branch_repo = get_default_worktree()?;
  let ignored_files: Vec<PathBuf> =
    get_ignored_files(&main_branch_repo, &args.exclude).map_err(|e| e.to_string())?;

  println!("ignored: {:?}", ignored_files);

  //TODO: Copy git ignored files from origin(main) branch

  //TODO: Execute create config commands
  return Ok(());
}

fn escape_branch_name(new_branch_name: &str) -> String {
  return str::replace(new_branch_name, "/", "-");
}

fn join_path(path: &Path, extension: &str) -> PathBuf {
  return path.join(extension);
}

fn create_new_worktree(bare_repo: &Repository, branch_name: &str) -> Result<Worktree, String> {
  let repo_path: &Path = bare_repo.path();
  let escaped_branch_name: String = escape_branch_name(branch_name);
  let new_worktree_path: PathBuf = join_path(repo_path, escaped_branch_name.as_str());

  let mut add_options = WorktreeAddOptions::new();
  add_options.checkout_existing(true);

  return match bare_repo.worktree(
    &escaped_branch_name,
    new_worktree_path.as_path(),
    Some(&add_options),
  ) {
    Ok(worktree) => Ok(worktree),
    Err(e) => Err(e.message().to_string()),
  };
}
