use std::{ffi::OsString, path::PathBuf};

pub(crate) trait PathBufExt {
  fn to_string(&self) -> Result<String, OsString>;
}

impl PathBufExt for PathBuf {
  fn to_string(&self) -> Result<String, OsString> {
    self.clone().into_os_string().into_string()
  }
}
