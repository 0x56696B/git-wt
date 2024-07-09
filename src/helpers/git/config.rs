use std::{
  fs::{create_dir_all, File},
  path::{Path, PathBuf},
};

use git2::{Config, ConfigLevel, Error, Repository};

use super::repo::get_repo_name;

/// This retuns the config for the repository
/// If values need to be queried, call .snapshot()
/// The config is a dedicated file for git-wt
///
/// This means the execution will not change, if the config is changed while the app is running
pub(crate) fn get_wt_config() -> Result<Config, String> {
  let mut config_path: PathBuf = get_config_path()?;
  config_path.set_file_name(".gitconfig_wt");

  if !config_path.exists() {
    let config_parent: &Path = config_path.parent().unwrap();

    let _ = create_dir_all(config_parent).map_err(|e| e.to_string());
    File::create(&config_path).map_err(|e| e.to_string())?;
  }

  // println!("{:?}", config_path);

  let mut config: Config =
    Config::open(config_path.as_path()).map_err(|e| e.message().to_string())?;

  if !config_path.exists() {
    config
      .add_file(config_path.as_path(), ConfigLevel::App, true)
      .map_err(|e| e.message().to_string())?;
  }

  return Ok(config);
}

pub(crate) fn get_config_entries(
  repo: &Repository,
  config_key: &str,
) -> Result<Vec<String>, String> {
  let config = get_wt_config()?;
  let repo_name = get_repo_name(&repo)?;

  let config_key: String = format!("{}.{}", repo_name, config_key);

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

fn get_config_path() -> Result<PathBuf, String> {
  let xdg_config: Result<PathBuf, Error> = Config::find_xdg();
  if !xdg_config.is_err() {
    return Ok(xdg_config.unwrap());
  }

  let user_config: Result<PathBuf, Error> = Config::find_global();
  if !user_config.is_err() {
    return Ok(user_config.unwrap());
  }

  return Err(String::from("Unable to find XDG or User git configuration"));
}
