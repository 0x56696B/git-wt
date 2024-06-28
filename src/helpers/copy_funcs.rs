use std::{
  fs::{copy, create_dir_all},
  path::{Path, PathBuf},
};

use crate::extensions::path_buf::PathBufExt;

/// Returns: Copied files in tuple (src, dest)
pub fn copy_files(
  root_src: &Path,
  root_dest: &Path,
  files_paths: Vec<&Path>,
) -> Result<(), String> {
  for file_path in files_paths {
    let src_path: PathBuf = root_src.join(file_path);
    let dest_path: PathBuf = root_dest.join(file_path);

    if !src_path.exists() {
      continue;
    }

    let dest_parent = dest_path
      .parent()
      .ok_or(format!("Error getting parent directory of {}", dest_path.display()))?;

    create_dir_all(&dest_parent)
      .map_err(|e| format!("Failed to create directory {}: {}", dest_parent.display(), e))?;

    copy(&src_path, &dest_path).map_err(|e| {
      format!("Failed to copy from {} to {}: {}", src_path.display(), dest_path.display(), e)
    })?;

    println!("Copied: {} -> {}", src_path.to_string().unwrap(), dest_path.to_string().unwrap());
  }

  return Ok(());
}
