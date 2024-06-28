use std::path::{Path, PathBuf};

pub(crate) fn escape_branch_name(new_branch_name: &str) -> String {
  return str::replace(new_branch_name, "/", "-");
}

pub(crate) fn join_path(path: &Path, extension: &str) -> PathBuf {
  return path.join(extension);
}
