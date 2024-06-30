use std::{collections::HashSet, fs::read_dir, path::PathBuf};

use crate::extensions::path_buf::PathBufExt;
use git2::{Repository, Status, StatusEntry, StatusOptions, StatusShow};

pub fn get_ignored_files(
  default_branch_repo: &Repository,
  filter_files: &Vec<String>,
) -> Result<HashSet<PathBuf>, String> {
  let mut status_opts = StatusOptions::new();
  status_opts.include_ignored(true).recurse_untracked_dirs(true).show(StatusShow::IndexAndWorkdir);

  let statuses =
    default_branch_repo.statuses(Some(&mut status_opts)).map_err(|e| e.message().to_string())?;
  let default_branch_path: String = default_branch_repo
    .workdir()
    .ok_or("Unable to find workdir for default branch")?
    .to_path_buf()
    .to_string()
    .unwrap();

  let ignored_files: HashSet<PathBuf> = statuses
    .iter()
    .filter_map(|x: StatusEntry| {
      if x.status() != Status::IGNORED {
        return None;
      };

      let absolute_path = format!("{}{}", &default_branch_path, x.path()?);
      return Some(PathBuf::from(absolute_path));
    })
    .flat_map(|path| {
      let mut paths: Vec<PathBuf> = Vec::new();
      collect_files_recursive(path, &mut paths, filter_files);

      return paths;
    })
    .collect::<HashSet<_>>();

  return Ok(ignored_files);
}

// TODO: Move into function that contains all ignored patterns from config
fn collect_files_recursive(path: PathBuf, files: &mut Vec<PathBuf>, filter: &Vec<String>) {
  for i in 0..filter.len() {
    if path.to_string_lossy().contains(&filter[i]) {
      return;
    }
  }

  if !path.is_dir() {
    files.push(path);
  } else {
    match read_dir(&path) {
      Ok(entries) => {
        for entry in entries {
          if let Ok(dir_entry) = entry {
            let entry_path = dir_entry.path();

            collect_files_recursive(entry_path, files, filter);
          }
        }
      }
      Err(_) => {}
    }
  }

  return;
}
