"""Unit tests for adapter file selection."""

from __future__ import annotations

from typing import cast

from compass.domain.analysis_context import AnalysisContext
from compass.domain.architecture_snapshot import ArchitectureSnapshot
from compass.domain.cluster import Cluster
from compass.domain.coupling_pair import CouplingPair
from compass.domain.file_score import FileScore
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot
from compass.file_selector import (
	RULES_SELECTION_CRITERIA,
	SUMMARY_SELECTION_CRITERIA,
	CoverageCategory,
	_RankedFile,
	apply_coverage,
	select_files,
)


def test_rules_selection_prioritizes_low_churn_centrality_and_coupling() -> None:
	context = _build_context(
		file_scores=[
			_build_file_score('src/service.py', centrality=0.82, churn=0.12, coupling_count=4),
			_build_file_score('src/hotspot.py', centrality=0.88, churn=0.94, coupling_count=1),
			_build_file_score('src/config.py', centrality=0.30, churn=0.04, coupling_count=1),
		],
		hotspots=['src/hotspot.py'],
	)

	selected = select_files(context, RULES_SELECTION_CRITERIA, 'generic')

	assert selected[0] == 'src/service.py'


def test_summary_selection_prioritizes_hotspots_plus_centrality() -> None:
	context = _build_context(
		file_scores=[
			_build_file_score('src/service.py', centrality=0.82, churn=0.12, coupling_count=4),
			_build_file_score('src/hotspot.py', centrality=0.88, churn=0.94, coupling_count=1),
			_build_file_score('src/config.py', centrality=0.30, churn=0.04, coupling_count=1),
		],
		hotspots=['src/hotspot.py'],
	)

	selected = select_files(context, SUMMARY_SELECTION_CRITERIA, 'generic')

	assert selected[0] == 'src/hotspot.py'


def test_apply_coverage_adds_missing_python_categories() -> None:
	context = _build_context(
		file_scores=[
			_build_file_score('src/service.py', centrality=0.95, churn=0.15, coupling_count=4),
			_build_file_score('src/config.py', centrality=0.40, churn=0.08, coupling_count=1),
			_build_file_score('src/api.py', centrality=0.50, churn=0.30, coupling_count=1),
			_build_file_score('src/cli.py', centrality=0.45, churn=0.20, coupling_count=1),
			_build_file_score('src/repository.py', centrality=0.43, churn=0.12, coupling_count=1),
			_build_file_score('src/models.py', centrality=0.39, churn=0.07, coupling_count=1),
		],
		hotspots=[],
	)

	selected = select_files(
		context,
		SUMMARY_SELECTION_CRITERIA.__class__(
			limit=1,
			centrality_weight=SUMMARY_SELECTION_CRITERIA.centrality_weight,
			hotspot_weight=SUMMARY_SELECTION_CRITERIA.hotspot_weight,
		),
		'python',
	)

	assert selected == [
		'src/service.py',
		'src/cli.py',
		'src/api.py',
		'src/repository.py',
		'src/models.py',
		'src/config.py',
	]


def test_apply_coverage_uses_language_specific_category_sets() -> None:
	context = _build_context(
		file_scores=[
			_build_file_score('src/service.ts', centrality=0.95, churn=0.15, coupling_count=4),
			_build_file_score('src/index.ts', centrality=0.44, churn=0.18, coupling_count=1),
			_build_file_score('src/api.ts', centrality=0.43, churn=0.21, coupling_count=1),
			_build_file_score('src/repository.ts', centrality=0.42, churn=0.19, coupling_count=1),
			_build_file_score('src/types.ts', centrality=0.41, churn=0.16, coupling_count=1),
			_build_file_score('src/config.ts', centrality=0.40, churn=0.14, coupling_count=1),
		],
		hotspots=[],
	)

	selected_typescript = select_files(
		context,
		SUMMARY_SELECTION_CRITERIA.__class__(
			limit=1,
			centrality_weight=SUMMARY_SELECTION_CRITERIA.centrality_weight,
			hotspot_weight=SUMMARY_SELECTION_CRITERIA.hotspot_weight,
		),
		'typescript',
	)
	selected_generic = select_files(
		context,
		SUMMARY_SELECTION_CRITERIA.__class__(
			limit=1,
			centrality_weight=SUMMARY_SELECTION_CRITERIA.centrality_weight,
			hotspot_weight=SUMMARY_SELECTION_CRITERIA.hotspot_weight,
		),
		'generic',
	)

	assert 'src/types.ts' in selected_typescript
	assert 'src/api.ts' in selected_typescript
	assert 'src/repository.ts' in selected_typescript
	assert 'src/types.ts' not in selected_generic
	assert selected_generic == ['src/service.ts', 'src/index.ts', 'src/config.ts']


def test_apply_coverage_preserves_existing_order_and_deduplicates() -> None:
	ranked_files = [
		_build_ranked_file('src/service.py', 1.0, 'service'),
		_build_ranked_file('src/cli.py', 0.8, 'entrypoint'),
		_build_ranked_file('src/config.py', 0.7, 'config'),
	]

	assert apply_coverage(
		['src/service.py', 'src/service.py'],
		ranked_files,
		'generic',
	) == ['src/service.py', 'src/cli.py', 'src/config.py']


def _build_context(file_scores: list[FileScore], hotspots: list[str]) -> AnalysisContext:
	coupling_pairs = [
		CouplingPair(file_a=file_score.path, file_b=paired_path, degree=1)
		for file_score in file_scores
		for paired_path in file_score.coupling_pairs
	]
	return AnalysisContext(
		architecture=ArchitectureSnapshot(
			file_scores=file_scores,
			coupling_pairs=coupling_pairs,
			clusters=[Cluster(id=0, files=tuple(file_score.path for file_score in file_scores))],
		),
		patterns={},
		git_patterns=GitPatternsSnapshot(
			hotspots=hotspots,
			stable_files=[],
			coupling_clusters=[],
		),
		docs={},
	)


def _build_file_score(path: str, centrality: float, churn: float, coupling_count: int) -> FileScore:
	return FileScore(
		path=path,
		churn=churn,
		age=1,
		centrality=centrality,
		cluster_id=0,
		coupling_pairs=tuple(f'dependency-{index}' for index in range(coupling_count)),
	)


def _build_ranked_file(path: str, score: float, category: CoverageCategory) -> _RankedFile:
	return _RankedFile(path=path, score=score, category=cast(CoverageCategory, category))
