from dataclasses import dataclass


@dataclass()
class ConfigArgs:
    current_working_dir: str
    add_commands: tuple[str, ...]
    remove_commands: tuple[str, ...]
    copy_exclude: tuple[str, ...]
    default_branch_name: str
    list: bool
