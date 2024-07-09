use std::{fs::copy, path::Path};

use crate::helpers::copy_funcs::copy_files;

use super::TestArgs;
pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let files = vec![Path::new("a"), Path::new("b"), Path::new("c")];
  let src = Path::new(".");
  let dest = Path::new("./copy_test");
  copy_files(src, dest, files);

  // let bare_repo: Repository = get_bare_git_repo().map_err(|e| e.to_string())?;
  // let add_cmd_entries = get_config_entries(&bare_repo, CONFIG_KEY_ADD_COMMANDS)?;
  // let repo_path = get_repo_path(&bare_repo)?;
  //
  // let _ = add_cmd_entries
  //   .iter()
  //   .map(|add_cmd: &String| {
  //     let (exec, args) = add_cmd.split_once(" ").unwrap_or((&add_cmd, ""));
  //
  //     let mut cmd = Command::new(&exec);
  //     cmd.current_dir(repo_path).stdout(Stdio::piped()).stderr(Stdio::piped()).arg(&args);
  //
  //     return cmd;
  //   })
  //   .collect::<Vec<Command>>()
  //   .iter_mut()
  //   .inspect(|cmd| {
  //     println!("Executing: {:?}", cmd);
  //   })
  //   .map_while(|cmd: &mut Command| {
  //     match cmd.output() {
  //       Ok(succ) => {
  //         io::stdout().write_all(&succ.stdout).unwrap();
  //
  //         return Some(());
  //       }
  //       Err(err) => {
  //         io::stderr().write_all(&err.to_string().as_bytes()).unwrap();
  //
  //         return None;
  //       }
  //     };
  //   })
  //   .collect::<Vec<()>>();

  return Ok(());
}
