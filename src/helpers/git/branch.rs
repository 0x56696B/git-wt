use git2::{Branch, BranchType, Commit, Oid, Repository, Worktree};

// TODO: Implement
pub(crate) fn get_repo_default_branch() -> String {
  return String::from("main");
}

//TODO: Implement
pub(crate) fn get_worktree_branch_name(_worktree: &Worktree) -> Result<String, String> {
  return Ok("feat/test".to_string());
}

pub(crate) fn detect_worktree_merged(
  bare_repo: &Repository,
  worktree_branch_name: &str,
  main_branch_name: &str,
) -> Result<bool, String> {
  let main_branch: Branch = bare_repo
    .find_branch(main_branch_name, BranchType::Local)
    .map_err(|e| e.message().to_string())?;
  let main_commit: Commit =
    main_branch.get().peel_to_commit().map_err(|e| e.message().to_string())?;

  let worktree_branch = bare_repo
    .find_branch(worktree_branch_name, BranchType::Local)
    .map_err(|e| e.message().to_string())?;
  let worktree_commit =
    worktree_branch.get().peel_to_commit().map_err(|e| e.message().to_string())?;

  let merge_base: Oid = bare_repo
    .merge_base(main_commit.id(), worktree_commit.id())
    .map_err(|e| e.message().to_string())?;

  return Ok(merge_base == worktree_commit.id());
}
