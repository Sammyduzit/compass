"""Select relevant files for adapter execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Literal

from compass.domain.analysis_context import AnalysisContext
from compass.domain.file_score import FileScore
from compass.language_detection import DetectedLanguage


CoverageCategory = Literal[
	'api',
	'config',
	'entrypoint',
	'model',
	'repository',
	'service',
	'types',
]


@dataclass(frozen=True)
class FileSelectionCriteria:
	"""Weights that define adapter-specific file ranking."""

	limit: int
	centrality_weight: float
	churn_weight: float = 0.0
	coupling_weight: float = 0.0
	hotspot_weight: float = 0.0
	prefer_low_churn: bool = False


@dataclass(frozen=True)
class _RankedFile:
	path: str
	score: float
	category: CoverageCategory | None


RULES_SELECTION_CRITERIA = FileSelectionCriteria(
	limit=6,
	centrality_weight=1.0,
	churn_weight=0.7,
	coupling_weight=0.8,
	prefer_low_churn=True,
)

SUMMARY_SELECTION_CRITERIA = FileSelectionCriteria(
	limit=6,
	centrality_weight=1.0,
	hotspot_weight=0.9,
)


def select_files(
	analysis_context: AnalysisContext,
	criteria: FileSelectionCriteria,
	language: DetectedLanguage,
) -> list[str]:
	"""Select and rank repository files for a downstream adapter."""

	ranked_files = _rank_files(analysis_context, criteria, language)
	selected_paths = [ranked.path for ranked in ranked_files[: criteria.limit]]
	return apply_coverage(selected_paths, ranked_files, language)


def apply_coverage(
	selected_paths: list[str],
	ranked_files: list[_RankedFile],
	language: DetectedLanguage,
) -> list[str]:
	"""Ensure the selection contains language-specific category representatives."""

	selected = _dedupe(selected_paths)
	required_categories = _coverage_categories(language)
	selected_categories = {
		category
		for path in selected
		for category in [_categorize_path(path, language)]
		if category is not None
	}

	for category in required_categories:
		if category in selected_categories:
			continue
		for ranked in ranked_files:
			if ranked.category != category or ranked.path in selected:
				continue
			selected.append(ranked.path)
			selected_categories.add(category)
			break

	return selected


def _rank_files(
	analysis_context: AnalysisContext,
	criteria: FileSelectionCriteria,
	language: DetectedLanguage,
) -> list[_RankedFile]:
	hotspots = set(analysis_context.git_patterns.hotspots)
	max_coupling = max(
		(
			len(file_score.coupling_pairs)
			for file_score in analysis_context.architecture.file_scores
		),
		default=1,
	)

	ranked_files = [
		_RankedFile(
			path=file_score.path,
			score=_score_file(file_score, hotspots, max_coupling, criteria),
			category=_categorize_path(file_score.path, language),
		)
		for file_score in analysis_context.architecture.file_scores
	]
	ranked_files.sort(key=lambda ranked: (-ranked.score, ranked.path))
	return ranked_files


def _score_file(
	file_score: FileScore,
	hotspots: set[str],
	max_coupling: int,
	criteria: FileSelectionCriteria,
) -> float:
	churn_signal = (
		1.0 - _clamp(file_score.churn) if criteria.prefer_low_churn else _clamp(file_score.churn)
	)
	coupling_signal = len(file_score.coupling_pairs) / max_coupling if max_coupling else 0.0
	hotspot_signal = 1.0 if file_score.path in hotspots else 0.0

	return (
		criteria.centrality_weight * _clamp(file_score.centrality)
		+ criteria.churn_weight * churn_signal
		+ criteria.coupling_weight * coupling_signal
		+ criteria.hotspot_weight * hotspot_signal
	)


def _coverage_categories(language: DetectedLanguage) -> tuple[CoverageCategory, ...]:
	if language == 'python':
		return ('entrypoint', 'api', 'service', 'repository', 'model', 'config')
	if language == 'typescript':
		return ('entrypoint', 'api', 'service', 'repository', 'types', 'config')
	return ('entrypoint', 'config')


def _categorize_path(path: str, language: DetectedLanguage) -> CoverageCategory | None:
	parts = tuple(part.lower() for part in PurePosixPath(path).parts)
	name = PurePosixPath(path).name.lower()
	stem = PurePosixPath(path).stem.lower()

	if name in {'main.py', 'app.py', 'cli.py', 'index.ts', 'index.js'} or stem == '__main__':
		return 'entrypoint'
	if 'api' in parts or 'routes' in parts or name in {'api.py', 'api.ts'}:
		return 'api'
	if 'service' in stem or 'services' in parts:
		return 'service'
	if 'repository' in stem or 'repositories' in parts or 'db' in parts:
		return 'repository'
	if 'config' in stem or 'settings' in stem:
		return 'config'
	if language == 'python' and ('model' in stem or 'models' in parts or 'schema' in stem):
		return 'model'
	if language == 'typescript' and ('type' in stem or 'types' in parts or name.endswith('.d.ts')):
		return 'types'
	return None


def _dedupe(paths: list[str]) -> list[str]:
	seen: set[str] = set()
	deduped: list[str] = []
	for path in paths:
		if path in seen:
			continue
		seen.add(path)
		deduped.append(path)
	return deduped


def _clamp(value: float) -> float:
	return max(0.0, min(1.0, value))
