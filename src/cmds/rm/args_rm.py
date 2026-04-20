from dataclasses import dataclass


@dataclass()
class RmArgs:
    branch_names: tuple[str, ...]
    current_working_dir: str
    force: bool
