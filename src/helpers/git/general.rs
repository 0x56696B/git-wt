pub(crate) fn escape_branch_name(new_branch_name: &str) -> String {
  return str::replace(new_branch_name, "/", "-");
}
