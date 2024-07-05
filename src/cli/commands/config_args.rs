use clap::Args;

/// Configure per-repo helpers and specfic behaviors
///
/// NOTE: Every option is overridden
#[derive(Args, Debug, Clone)]
pub struct ConfigArgs {
  /// Configure commands to run after every successfull new worktree. Automatically ran after
  /// `git-wt add`
  ///
  /// NOTE: Multiple commands will be executed with `&&`
  #[arg(short = 'a', long = "add-command", value_name = "CMD")]
  pub create_commands: Vec<String>,

  /// Configure commands to run after every successfull worktree removal. Automatically ran after
  /// `git-wt rm`
  ///
  /// NOTE: Multiple commands will be executed with `&&`
  #[arg(short = 'r', long = "rm-command", value_name = "CMD")]
  pub remove_commands: Vec<String>,

  /// Configure default files to exclude, per repo, when creating a new worktree with `git-wt`
  ///
  /// NOTE: This command will store different configuration for each repository
  ///
  /// Example: ["node_modules", "cache"]
  ///
  /// The `git wt add` wouldn't need `--exclude "node_modules" --exclude "cache"` every time it's ran in the configured repo
  #[arg(short = 'e', long = "copy-exclude", value_name = "EXCLUDE_PATTERN")]
  pub copy_exclude: Vec<String>,

  /// Configure commands to run to open a worktree
  #[arg(short, long)]
  pub open_commands: Vec<String>,
}
