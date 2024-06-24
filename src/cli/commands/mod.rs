pub mod add;

use clap::{Args, Subcommand};

#[derive(Debug, Clone, Subcommand)]
pub enum Commands {
  Add(AddArgs),
  Rm(RmArgs),
  Config(ConfigArgs),
  Open(OpenArgs),
}

/// Add a new folder with a worktree
#[derive(Args, Debug, Clone)]
pub struct AddArgs {
  /// The new branch's name
  ///
  /// NOTE: Slashes `/` will be replaced with dash `-` to avoid folder nesting
  new_branch_name: String,

  /// Force checkout, even if the branch already exists locally
  #[arg(short, long)]
  force: bool,
}

/// Remove a worktree after it's been merged or no longer needed
#[derive(Args, Debug, Clone)]
pub struct RmArgs {}

/// Configure per-repo helpers and specfic behaviors
#[derive(Args, Debug, Clone)]
pub struct ConfigArgs {
  /// Configure commands to run after every successfull new worktree. Automatically ran after
  /// `git-wt add`
  #[arg(short, long)]
  create_commands: Vec<String>,

  /// Configure commands to run after every successfull worktree removal. Automatically ran after
  /// `git-wt rm`
  #[arg(short, long)]
  remove_commands: Vec<String>,

  /// Configure commands to run to open a worktree
  #[arg(short, long)]
  open_commands: Vec<String>,
}

/// Custom commands to execute to open the new worktree
///
/// Example: `code ${new-worktree}` to open VSCode in a worktree
#[derive(Args, Debug, Clone)]
pub struct OpenArgs {}
