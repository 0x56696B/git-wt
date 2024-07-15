use std::{collections::HashSet, fs::read_dir, path::PathBuf, str::FromStr};

use crate::extensions::path_buf::PathBufExt;
use git2::{Repository, Status, StatusEntry, StatusOptions, StatusShow};

/// Get files to later copy to new Worktree dir
/// Files will be returned relative to worktree
pub fn get_files_for_cp(
  default_branch_repo: &Repository,
  filter_files: &Vec<String>,
  excluded_dirs: &Vec<String>,
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
    // .inspect(|x| {
    //   println!("Non-ignored file: {:?}", x.path());
    // })
    .filter(|x| x.status() == Status::IGNORED)
    // .inspect(|x| {
    //   println!("Ignored file: {:?}", x.path());
    // })
    .map(|x: StatusEntry| {
      let entry_path = x.path().unwrap();

      let absolute_path = format!("{}{}", &default_branch_path, entry_path);
      return PathBuf::from(absolute_path);
    })
    // Git ignored files
    .flat_map(|path_buf: PathBuf| {
      let mut paths: Vec<PathBuf> = Vec::new();
      collect_files_recursive(path_buf, &mut paths, filter_files);

      return paths;
    })
    // Config ignored files
    .filter(|path_buf: &PathBuf| {
      let path = &path_buf.to_string_lossy();

      return !excluded_dirs.iter().any(|excluded| path.contains(excluded));
    })
    .map(|path_buf: PathBuf| {
      let path = path_buf.to_string().unwrap();
      return PathBuf::from_str(&path[default_branch_path.len()..path.len()]).unwrap();
    })
    // .inspect(|x: &PathBuf| {
    //   println!("{:?}", x.display());
    // })
    .collect::<HashSet<_>>();

  return Ok(ignored_files);
}

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
