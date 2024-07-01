use std::path::PathBuf;

use git2::{Config, Error};

pub(crate) fn get_config() -> Result<PathBuf, String> {
  let xdg_config: Result<PathBuf, Error> = Config::find_xdg();
  if !xdg_config.is_err() {
    return Ok(xdg_config.unwrap());
  }

  return Config::find_global().map_err(|e| e.message().to_string());
}
