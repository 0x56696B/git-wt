from dataclasses import dataclass


@dataclass()
class WorktreeInfo:
    name: str
    path: str
    is_prunable: bool
    has_unmerged_commits: bool
