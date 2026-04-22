from dataclasses import dataclass
from pathlib import Path


@dataclass()
class CloneArgs:
    repository_link: str
    dest: Path
