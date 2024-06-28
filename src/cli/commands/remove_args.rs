use clap::Args;

/// Remove a worktree after it's been merged or no longer needed
#[derive(Args, Debug, Clone)]
pub struct RmArgs {
  /// Force checkout, even if the branch already exists locally
  #[arg(short, long)]
  pub force: bool,
}
