use git2::Repository;

use crate::helpers::git::{repo::get_bare_git_repo, worktrees::remove_worktree};

use super::remove_args::RmArgs;

/// Function to execute Command::Rm
pub fn remove_command(args: RmArgs) -> Result<(), String> {
  let bare_repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;

  //TODO: Execute remove config commands
  return remove_worktree(&bare_repo, args.worktree_name.as_str(), args.force)
    .map_err(|e| e.to_string());
}
