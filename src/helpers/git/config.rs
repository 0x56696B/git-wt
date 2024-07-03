use std::{
  fs::{create_dir_all, File},
  path::{Path, PathBuf},
};

use git2::{Config, ConfigLevel, Error};

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
