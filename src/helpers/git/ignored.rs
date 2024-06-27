use git2::{Repository, Status, StatusOptions};

pub fn get_ignored_files(default_branch_repo: &Repository) -> Result<Vec<String>, String> {
  let mut status_opts = StatusOptions::new();
  status_opts
    .include_ignored(true)
    .recurse_ignored_dirs(true)
    // .recurse_untracked_dirs(true)
    .show(git2::StatusShow::IndexAndWorkdir);

  let statuses =
    default_branch_repo.statuses(Some(&mut status_opts)).map_err(|e| e.message().to_string())?;

  let ignored_paths: Vec<String> = statuses
    .iter()
    .filter(|x| x.status() == Status::IGNORED)
    .map(|x| return x.path().unwrap().to_owned())
    .collect();

  return Ok(ignored_paths);
}
