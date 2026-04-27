"""Centralized path helpers for Compass outputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


COMPASS_DIRNAME = '.compass'
OUTPUT_DIRNAME = 'output'
TEMPLATES_DIRNAME = 'prompts/templates'


def templates_dir() -> Path:
	return Path(__file__).parent / TEMPLATES_DIRNAME


@dataclass(frozen=True)
class CompassPaths:
	"""Computed paths under a target repository's .compass directory."""

	target_path: Path

	@property
	def compass_dir(self) -> Path:
		return self.target_path / COMPASS_DIRNAME

	@property
	def analysis_context(self) -> Path:
		return self.compass_dir / 'analysis_context.json'

	@property
	def repo_state(self) -> Path:
		return self.compass_dir / 'repo_state.json'

	@property
	def output_dir(self) -> Path:
		return self.compass_dir / OUTPUT_DIRNAME

	@property
	def rules_yaml(self) -> Path:
		return self.output_dir / 'rules.yaml'

	@property
	def summary_md(self) -> Path:
		return self.output_dir / 'summary.md'


def compass_paths(target_path: str | Path) -> CompassPaths:
	return CompassPaths(Path(target_path))
