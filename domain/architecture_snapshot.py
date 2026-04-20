from dataclasses import dataclass

from domain.coupling_pair import CouplingPair
from domain.file_score import FileScore


@dataclass(frozen=True)
class Cluster:
    id: int
    files: list[str]

@dataclass(frozen=True)
class ArchitectureSnapshot:
    file_scores: list[FileScore]
    coupling_pairs: list[CouplingPair]
    clusters: list[Cluster]
