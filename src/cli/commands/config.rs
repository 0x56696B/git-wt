use git2::{Config, Repository};

use crate::helpers::git::{
  config::get_wt_config,
  config_keys::{CONFIG_KEY_ADD_COMMANDS, CONFIG_KEY_EXCLUDE_FILES, CONFIG_KEY_RM_COMMANDS},
  repo::{get_bare_git_repo, get_repo_name},
};

use super::config_args::ConfigArgs;

/// Function to execute Command::Config
pub fn config_command(args: ConfigArgs) -> Result<(), String> {
  let bare_repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;

  let mut config: Config = get_wt_config().unwrap();
  let repo_name = get_repo_name(&bare_repo)?;

  if args.create_commands.len() != 0 {
    let _ =
      save_multi_var_config(&mut config, repo_name, CONFIG_KEY_ADD_COMMANDS, args.create_commands)?;
  }

  if args.remove_commands.len() != 0 {
    let _ =
      save_multi_var_config(&mut config, repo_name, CONFIG_KEY_RM_COMMANDS, args.remove_commands)?;
  }

  if args.copy_exclude.len() != 0 {
    let _ =
      save_multi_var_config(&mut config, repo_name, CONFIG_KEY_EXCLUDE_FILES, args.copy_exclude)?;
  }

  return Ok(());
}

fn save_multi_var_config(
  config: &mut Config,
  repo_name: &str,
  config_key: &str,
  values: Vec<String>,
) -> Result<(), String> {
  let config_key: String = format!("{}.{}", repo_name, config_key);

  let _ = config.remove_multivar(&config_key, ".*");

  for val in values {
    let _ =
      config.set_multivar(&config_key, &config_key, &val).map_err(|e| e.message().to_string());
  }

  return Ok(());
}
