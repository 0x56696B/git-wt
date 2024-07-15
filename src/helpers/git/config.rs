use std::{
  fs::{create_dir_all, File},
  io::{self, Write},
  path::{Path, PathBuf},
  process::{Command, Stdio},
};

use git2::{Config, ConfigLevel, Error, Repository};

use super::repo::get_repo_name;

/// This retuns the config for the repository
/// The config is a dedicated file for git-wt
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

pub(crate) fn execute_config_cmds(
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
