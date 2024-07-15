use git2::Repository;

use crate::helpers::git::{
  config::{add_config_entry, get_config_entry},
  config_keys::CONFIG_KEY_DEFAULT_BRANCH,
  repo::{get_bare_git_repo, get_repo_name},
};

use super::TestArgs;
pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let bare_repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;

  let repo_name: &str = get_repo_name(&bare_repo)?;

  // let _ = add_config_entry(repo_name, CONFIG_KEY_DEFAULT_BRANCH, "main");
  let config_entry = get_config_entry(repo_name, CONFIG_KEY_DEFAULT_BRANCH);
  if config_entry.is_ok() {
    println!("{}", config_entry.unwrap());
  }

  return Ok(());
}
