use git2::{Config, Repository};

use crate::helpers::git::{
  config::get_wt_config,
  repo::{get_bare_git_repo, get_repo_name},
};

use super::TestArgs;

pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let bare_repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;
  let mut config: Config = get_wt_config().unwrap();

  let repo_name = get_repo_name(&bare_repo)?;
  let config_key = format!("{}.test", repo_name);
  let _ = config.set_str(&config_key, "tested").map_err(|e| e.message().to_string())?;

  let mut entries = config.entries(None).unwrap();
  while let Some(entry) = entries.next() {
    let entry = entry.unwrap();
    println!("{} => {}", entry.name().unwrap(), entry.value().unwrap());
  }

  return Ok(());
}
