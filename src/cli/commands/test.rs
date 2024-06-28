use std::{
  collections::HashSet,
  path::{Path, PathBuf},
};

use crate::helpers::{
  copy_funcs::copy_files,
  git::{get_default_worktree, ignored::get_ignored_files},
};

use super::TestArgs;

pub fn test_command(_args: TestArgs) -> Result<(), String> {
  let main_branch_repo = get_default_worktree()?;
  let to_ignore = vec![String::from("node_modules"), String::from("cache")];
  let ignored_files: HashSet<PathBuf> =
    get_ignored_files(&main_branch_repo, &to_ignore).map_err(|e| e.to_string())?;

  // for file in ignored_files.iter() {
  //   println!("to be copied over: {:?}", file);
  // }

  let root_src = main_branch_repo.workdir().ok_or("Unable to find workdir for default branch")?;
  let root_dest = Path::new("/Users/viko/personal/dotfiles-bare/feat-test");
  let file_paths = ignored_files.iter().map(|file| file.as_path()).collect();

  copy_files(root_src, root_dest, file_paths).map_err(|e| e)?;

  return Ok(());
}
