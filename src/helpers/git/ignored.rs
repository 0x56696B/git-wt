use std::path::PathBuf;

use git2::{Repository, Status, StatusOptions, StatusShow};

pub fn get_ignored_files(
  default_branch_repo: &Repository,
  filter_files: &Vec<String>,
) -> Result<Vec<PathBuf>, String> {
  let mut status_opts = StatusOptions::new();
  status_opts.include_ignored(true).recurse_untracked_dirs(true).show(StatusShow::IndexAndWorkdir);

  let statuses =
    default_branch_repo.statuses(Some(&mut status_opts)).map_err(|e| e.message().to_string())?;

  let ignored_files: Vec<PathBuf> = statuses
    .iter()
    .filter_map(|x| {
      if x.status() != Status::IGNORED {
        return None;
      };

      // TODO: Move into function that contains all ignored patterns from config
      let path = x.path()?;

      for i in 1..filter_files.len() {
        if path.contains(&filter_files[i]) {
          return None;
        }
      }

      return Some(PathBuf::from(path));
    })
    .collect();

  return Ok(ignored_files);
}
