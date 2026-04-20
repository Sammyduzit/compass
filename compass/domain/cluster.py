from dataclasses import dataclass


@dataclass(frozen=True)
class Cluster:
    id: int
    files: list[str]
