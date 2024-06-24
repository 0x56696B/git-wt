mod cli;

use cli::{
  commands::{add::add_command, Commands},
  Cli,
};

fn main() {
  let args = Cli::new();
  match args.command {
    Commands::Add(args) => add_command(args),
    Commands::Rm(args) => todo!(),
    Commands::Config(args) => todo!(),
    Commands::Open(args) => todo!(),
  }
}
