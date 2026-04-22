from dataclasses import dataclass


@dataclass()
class PullArgs:
    branch_name: str
    current_working_dir: str
