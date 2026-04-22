from dataclasses import dataclass

from compass.domain.coupling_pair import CouplingPair
from compass.domain.file_score import FileScore
from compass.domain.cluster import Cluster


@dataclass(frozen=True)
class ArchitectureSnapshot:
	file_scores: list[FileScore]
	coupling_pairs: list[CouplingPair]
	clusters: list[Cluster]
