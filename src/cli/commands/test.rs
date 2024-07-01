use crate::helpers::git::config::get_config;
use std::path::PathBuf;

use super::TestArgs;

pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let config: Result<PathBuf, String> = get_config();

  println!("{:?}", config);

  return Ok(());
}
