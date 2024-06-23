mod cli;

use cli::Cli;

fn main() {
    let args = Cli::new();

    println!("Hello {:?}!", args.command);
}
