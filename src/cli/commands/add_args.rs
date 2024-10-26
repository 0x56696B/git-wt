use clap::Args;

/// Add a new folder with a worktree
#[derive(Args, Debug, Clone)]
pub struct AddArgs {
  /// The new branch's name
  ///
  /// NOTE: Slashes `/` will be replaced with dash `-` to avoid folder nesting
  pub new_branch_name: String,

  /// Force checkout, even if the branch already exists locally
  #[arg(short = 'f', long)]
  pub force: bool,

  /// Pattern to ignore when copying hidden files
  ///
  /// Example: node_modules, dist, target, bin, etc.
  /// WARNING: This implies that configuration excluded files will be ignored
  #[arg(long, short = 'e')]
  pub exclude: Vec<String>,

  /// Update branch from which it will be derived, before creating the new worktree
  #[arg(long, short = 'u')]
  pub update_branch: bool,

  /// Specify from which branch to derive
  /// If not specified, will default to default branch (usually master or main)
  /// FIXME: NOT IMPLEMENTED YET
  #[arg(long, short = 'b')]
  pub derive_branch: String,
}
