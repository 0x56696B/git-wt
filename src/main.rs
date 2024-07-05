mod cli;
mod extensions;
mod helpers;

use cli::{
  commands::{
    add::add_command, config::config_command, remove::remove_command, test::test_command, Commands,
  },
  Cli,
};

fn main() {
  let args = Cli::new();

  let command_execution: Result<(), String> = match args.command {
    Commands::Test(args) => test_command(args),
    Commands::Add(args) => add_command(args),
    Commands::Rm(args) => remove_command(args),
    Commands::Config(args) => config_command(args),
    Commands::Open(_args) => todo!(),
  };

  match command_execution {
    Ok(()) => return,
    Err(err) => {
      println!("An error occured: {}", err)
    }
  }
}
