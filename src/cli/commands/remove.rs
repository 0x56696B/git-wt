use git2::{Repository, Worktree};

use crate::helpers::git::{
  branch::{detect_wt_merged, get_default_branch_name, get_wt_branch_name},
  config::execute_config_cmds,
  config_keys::CONFIG_KEY_RM_COMMANDS,
  repo::{get_bare_git_repo, get_repo_name},
  worktrees::{get_worktree, remove_worktree},
};

use super::remove_args::RmArgs;

/// Function to execute Command::Rm
pub fn remove_command(args: RmArgs) -> Result<(), String> {
  let repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;
  let repo_name: &str = get_repo_name(&repo)?;
  let default_branch_name: String = get_default_branch_name(repo_name)?;

  for worktree_name in args.worktree_names {
    let wt: Worktree = get_worktree(&repo, &worktree_name)?;
    let _ = wt.validate().map_err(|e| e.message().to_string())?;

    let wt_name: &str = wt.name().ok_or("Unable to get worktree name")?;
    let wt_path: &str = wt.path().to_str().ok_or("Unable to get Worktree path".to_string())?;

    if !args.force {
      let wt_branch_name = get_wt_branch_name(&wt.path())?;
      let merged: bool = detect_wt_merged(&repo, &wt_branch_name, &default_branch_name)?;

      if !merged {
        return Err(format!("Worktree {0} has not been merged to {1} branch. Use --force to override or merge it with {1}", &wt_name, &default_branch_name));
      }
    }

    let _ = execute_config_cmds(repo_name, wt_path, CONFIG_KEY_RM_COMMANDS)?;
    println!("Successfully executed configured commands for remove");

    let _ = remove_worktree(&wt_name, args.force).map_err(|e| e.to_string())?;
    println!("Successfully removed worktree");

    // let _ = prune_worktree(&wt, args.force).map_err(|e| e.to_string())?;
  }

  return Ok(());
}
