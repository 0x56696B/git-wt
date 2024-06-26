mod cli;
mod helpers;

use cli::{
  commands::{add::add_command, Commands},
  Cli,
};

fn main() {
  let args = Cli::new();
  let command_execution: Result<(), String> = match args.command {
    Commands::Add(args) => add_command(args),
    Commands::Rm(_args) => todo!(),
    Commands::Config(_args) => todo!(),
    Commands::Open(_args) => todo!(),
  };

  match command_execution {
    Ok(()) => return,
    Err(err) => {
      println!("An error occured: {}", err)
    }
  }
}
