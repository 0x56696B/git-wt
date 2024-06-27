use crate::helpers::git::{get_default_worktree, ignored::get_ignored_files};

use super::TestArgs;

pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let main_branch_repo = get_default_worktree()?;
  let ignored_files: Vec<String> =
    get_ignored_files(&main_branch_repo).map_err(|e| e.to_string())?;

  for file in ignored_files.iter() {
    println!("ignored: {:?}", file);
  }


  return Ok(());
}
