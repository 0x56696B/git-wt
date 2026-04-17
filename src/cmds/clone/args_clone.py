from dataclasses import dataclass


@dataclass()
class CloneArgs:
    repository_link: str
    dest: str

