use clap::Args;

/// Remove a worktree after it's been merged or no longer needed
#[derive(Args, Debug, Clone)]
pub struct RmArgs {
  /// Path to the worktree to remove
  /// This is the path you see at the git root, not the branch name (example: feat-feature-1)
  ///
  /// WARNING: Will fail, if it detects worktree isn't merged to default branch (main, for example)
  pub worktree_names: Vec<String>,

  /// Force removal, even if not merged
  ///
  /// WARNING: This disables the merge detection and prune-ability check with default branch (main, for example)
  #[arg(short, long)]
  pub force: bool,
}
