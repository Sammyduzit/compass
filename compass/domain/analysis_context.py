from dataclasses import dataclass

from compass.domain.architecture_snapshot import ArchitectureSnapshot
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot


@dataclass(frozen=True)
class AnalysisContext:
    architecture: ArchitectureSnapshot
    patterns: dict[str, list[str]]
    git_patterns: GitPatternsSnapshot
    docs: dict[str, str]
