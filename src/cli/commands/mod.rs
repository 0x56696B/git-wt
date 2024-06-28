pub mod add;
pub mod add_args;
pub mod remove;
pub mod remove_args;
pub mod test;

use add_args::AddArgs;
use clap::{Args, Subcommand};
use remove_args::RmArgs;

#[derive(Debug, Clone, Subcommand)]
pub enum Commands {
  Test(TestArgs),
  Add(AddArgs),
  Rm(RmArgs),
  Config(ConfigArgs),
  Open(OpenArgs),
}

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

/// Development only
/// Used for testing functionality while developing
#[derive(Args, Debug, Clone)]
pub struct TestArgs {}
