use clap::Args;

/// Add a new folder with a worktree
#[derive(Args, Debug, Clone)]
pub struct AddArgs {
  /// The new branch's name
  ///
  /// NOTE: Slashes `/` will be replaced with dash `-` to avoid folder nesting
  pub new_branch_name: String,

  /// Force checkout, even if the branch already exists locally
  #[arg(short, long)]
  pub force: bool,

  /// Pattern to ignore when copying hidden files
  ///
  /// Example: node_modules, dist, target, bin, etc.
  /// WARNING: This implies that configuration excluded files will be ignored
  #[arg(long)]
  pub exclude: Vec<String>,
}
