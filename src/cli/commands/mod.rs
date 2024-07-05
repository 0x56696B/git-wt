pub mod add;
pub mod add_args;
pub mod config;
pub mod config_args;
pub mod remove;
pub mod remove_args;
pub mod test;

use add_args::AddArgs;
use clap::{Args, Subcommand};
use config_args::ConfigArgs;
use remove_args::RmArgs;

#[derive(Debug, Clone, Subcommand)]
pub enum Commands {
  Test(TestArgs),
  Add(AddArgs),
  Rm(RmArgs),
  Config(ConfigArgs),
  /// Commands to run to switch worktrees
  ///
  /// Example: docker compose down && tmux attach_window? something...
  // Switch(SwitchArgs)
  Open(OpenArgs),
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
