use std::{
  collections::HashSet,
  io::{self, Write},
  path::PathBuf,
  process::{Command, Stdio},
};

use git2::{Repository, Worktree};

use super::AddArgs;
use crate::helpers::{
  copy_funcs::copy_files,
  git::{
    config::{get_config_entries, get_wt_config},
    config_keys::{CONFIG_KEY_ADD_COMMANDS, CONFIG_KEY_EXCLUDE_FILES},
    ignored::get_files_cp,
    repo::{get_bare_git_repo, get_repo_name},
    worktrees::{create_new_worktree, get_default_worktree, get_worktree_path},
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
    get_files_cp(&main_branch_repo, &args.exclude, &excluded_files).map_err(|e| e.to_string())?;

  let root_src = main_branch_repo.workdir().ok_or("Unable to find workdir for default branch")?;
  let root_dest = get_worktree_path(&worktree);
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

fn execute_config_cmds(
  repo: &Repository,
  exec_path: &str,
  config_key: &str,
) -> Result<Vec<()>, String> {
  return Ok(
    get_config_entries(&repo, config_key)?
      .iter()
      .map(|add_cmd: &String| {
        let (exec, args) = add_cmd.split_once(" ").unwrap_or((&add_cmd, ""));

        let mut cmd = Command::new(&exec);
        cmd.current_dir(exec_path).stdout(Stdio::piped()).stderr(Stdio::piped()).arg(&args);

        return cmd;
      })
      .collect::<Vec<Command>>()
      .iter_mut()
      .inspect(|cmd| println!("Executing: {:?}", cmd))
      .map_while(|cmd: &mut Command| {
        match cmd.output() {
          Ok(succ) => {
            io::stdout().write_all(&succ.stdout).unwrap();

            return Some(());
          }
          Err(err) => {
            io::stderr().write_all(&err.to_string().as_bytes()).unwrap();

            return None;
          }
        };
      })
      .collect::<Vec<()>>(),
  );
}
