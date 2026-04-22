from dataclasses import dataclass


@dataclass()
class DestroyArgs:
    directory: str
    force: bool
