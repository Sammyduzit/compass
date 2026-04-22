from dataclasses import dataclass


@dataclass(frozen=True)
class GitPatternsSnapshot:
	hotspots: list[str]
	stable_files: list[str]
	coupling_clusters: list[list[str]]
