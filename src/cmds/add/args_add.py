from dataclasses import dataclass, field


@dataclass()
class AddArgs:
    new_branch_name: str
    derive_from_branch: str = "main"
    should_nest_dirs: bool = False
    exclude: list[str] = field(default_factory=list)
    _force: bool = False
