use std::{
  fs::{copy, create_dir_all},
  path::{Path, PathBuf},
};

/// Returns: Copied files in tuple (src, dest)
pub fn copy_files(
  root_src: &Path,
  root_dest: &Path,
  files: Vec<&Path>,
) -> Vec<Result<String, String>> {
  return files
    .iter()
    .map(|path| {
      let src: PathBuf = root_src.join(path);
      let dest: PathBuf = root_dest.join(path);

      return (src, dest);
    })
    // .inspect(|(src, dest)| {
    //   println!("Do we even get here? {:?}: {:?}", &src.display(), &dest.display());
    // })
    .filter(|(src, _dest)| src.exists())
    .map_while(|(src, dest): (PathBuf, PathBuf)| -> Option<(PathBuf, PathBuf)> {
      let dest_parent = dest.parent();
      if dest_parent.is_none() {
        println!("Unable to get parent dir for {:?}", &dest.display());
        return None;
      }

      let create_res = create_dir_all(dest_parent.unwrap());
      if create_res.is_err() {
        return None;
      }

      return Some((src, dest));
    })
    // .inspect(|(src, dest)| {
    //   println!("Ready for copying: {:?} - {:?}", &src.display(), &dest.display());
    // })
    .map(|(src, dest)| -> Result<String, String> {
      let copy_res = copy(&src, &dest)
        .map(|_| format!("Copied: {:?} -> {:?}", src.to_string_lossy(), dest.to_string_lossy()))
        .map_err(|e| format!("Failed to copy from {} to {}: {}", src.display(), dest.display(), e));

      return copy_res;
    })
    .inspect(|copy_res: &Result<String, String>| match copy_res {
      Ok(succ) => println!("{}", succ),
      Err(err) => println!("{}", err),
    })
    .collect::<Vec<Result<String, String>>>();
}
