from dataclasses import dataclass


@dataclass(frozen=True)
class FileScore:
	path: str
	churn: float
	age: int
	centrality: float
	cluster_id: int
	coupling_pairs: list[str]
