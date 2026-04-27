"""Unit tests for the Compass runner."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from compass.config import CompassConfig
from compass.domain.analysis_context import AnalysisContext
from compass.domain.architecture_snapshot import ArchitectureSnapshot
from compass.domain.cluster import Cluster
from compass.domain.coupling_pair import CouplingPair
from compass.domain.file_score import FileScore
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot
from compass.errors import AdapterError, CollectorError
from compass.runner import (
	_build_orchestrator,
	_call_async_method,
	_collect_analysis_context,
	run,
)


def _build_analysis_context() -> AnalysisContext:
	return AnalysisContext(
		architecture=ArchitectureSnapshot(
			file_scores=[
				FileScore(
					path='src/app.py',
					churn=0.7,
					age=14,
					centrality=0.6,
					cluster_id=1,
					coupling_pairs=['src/utils.py'],
				)
			],
			coupling_pairs=[
				CouplingPair(file_a='src/app.py', file_b='src/utils.py', degree=3)
			],
			clusters=[Cluster(id=1, files=['src/app.py', 'src/utils.py'])],
		),
		patterns={'naming': ['snake_case']},
		git_patterns=GitPatternsSnapshot(
			hotspots=['src/app.py'],
			stable_files=['src/utils.py'],
			coupling_clusters=[['src/app.py', 'src/utils.py']],
		),
		docs={'README.md': 'Project summary'},
	)


def test_runner_skips_phase_one_when_cache_is_fresh(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config = CompassConfig(
		target_path=str(tmp_path),
		adapters=['rules', 'summary'],
		provider='claude',
		lang='auto',
		reanalyze=False,
	)
	analysis_context = _build_analysis_context()
	(tmp_path / '.compass').mkdir()
	(tmp_path / '.compass' / 'analysis_context.json').write_text('{}', encoding='utf-8')
	calls: list[tuple[str, object]] = []

	async def fake_check_prerequisites() -> None:
		calls.append(('prerequisites', None))

	def fake_detect_language(passed_config: CompassConfig, target_path: Path) -> str:
		calls.append(('language', target_path))
		assert passed_config == config
		return 'python'

	async def fake_collect_analysis_context(
		passed_config: CompassConfig,
		language: str,
	) -> AnalysisContext:
		calls.append(('collect', language))
		return _build_analysis_context()

	async def fake_run_adapters(
		passed_config: CompassConfig,
		passed_context: object,
		language: str,
	) -> list[str]:
		calls.append(('adapters', language))
		assert passed_config == config
		assert passed_context == analysis_context
		return ['rules', 'summary']

	monkeypatch.setattr('compass.runner._check_prerequisites', fake_check_prerequisites)
	monkeypatch.setattr('compass.runner._detect_language', fake_detect_language)
	monkeypatch.setattr('compass.runner.is_stale', lambda target_path: False)
	monkeypatch.setattr(
		'compass.runner.read_analysis_context', lambda target_path: analysis_context
	)
	monkeypatch.setattr('compass.runner._collect_analysis_context', fake_collect_analysis_context)
	monkeypatch.setattr('compass.runner._run_adapters', fake_run_adapters)

	result = asyncio.run(run(config))

	assert result == ['rules', 'summary']
	assert calls == [
		('prerequisites', None),
		('language', tmp_path),
		('adapters', 'python'),
	]


def test_runner_runs_phase_one_when_stale(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config = CompassConfig(
		target_path=str(tmp_path),
		adapters=['rules'],
		provider='codex',
		lang='auto',
		reanalyze=False,
	)
	collected_context = _build_analysis_context()
	writes: list[tuple[str, object]] = []

	async def fake_check_prerequisites() -> None:
		return None

	def fake_detect_language(passed_config: CompassConfig, target_path: Path) -> str:
		return 'typescript'

	async def fake_collect_analysis_context(
		passed_config: CompassConfig,
		language: str,
	) -> AnalysisContext:
		assert passed_config == config
		assert language == 'typescript'
		return collected_context

	async def fake_run_adapters(
		passed_config: CompassConfig,
		passed_context: object,
		language: str,
	) -> list[str]:
		assert passed_context == collected_context
		assert language == 'typescript'
		return ['rules']

	monkeypatch.setattr('compass.runner._check_prerequisites', fake_check_prerequisites)
	monkeypatch.setattr('compass.runner._detect_language', fake_detect_language)
	monkeypatch.setattr('compass.runner.is_stale', lambda target_path: True)
	monkeypatch.setattr('compass.runner._collect_analysis_context', fake_collect_analysis_context)
	monkeypatch.setattr(
		'compass.runner.write_analysis_context',
		lambda target_path, analysis_context: writes.append(('context', analysis_context)),
	)
	monkeypatch.setattr(
		'compass.runner.write_current_repo_state',
		lambda target_path: writes.append(('repo_state', target_path)),
	)
	monkeypatch.setattr('compass.runner._run_adapters', fake_run_adapters)

	result = asyncio.run(run(config))

	assert result == ['rules']
	assert writes == [('context', collected_context), ('repo_state', tmp_path)]


def test_runner_reanalyze_forces_phase_one_even_when_cache_is_fresh(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config = CompassConfig(
		target_path=str(tmp_path),
		adapters=['summary'],
		provider=None,
		lang='python',
		reanalyze=True,
	)
	(tmp_path / '.compass').mkdir()
	(tmp_path / '.compass' / 'analysis_context.json').write_text('{}', encoding='utf-8')
	calls: list[str] = []

	async def fake_check_prerequisites() -> None:
		return None

	async def fake_collect_analysis_context(
		passed_config: CompassConfig,
		language: str,
	) -> AnalysisContext:
		calls.append(language)
		return _build_analysis_context()

	async def fake_run_adapters(
		passed_config: CompassConfig,
		passed_context: object,
		language: str,
	) -> list[str]:
		assert passed_context == _build_analysis_context()
		assert language == 'python'
		return ['summary']

	monkeypatch.setattr('compass.runner._check_prerequisites', fake_check_prerequisites)
	monkeypatch.setattr(
		'compass.runner._detect_language', lambda passed_config, target_path: 'python'
	)
	monkeypatch.setattr('compass.runner._collect_analysis_context', fake_collect_analysis_context)
	monkeypatch.setattr(
		'compass.runner.write_analysis_context', lambda target_path, analysis_context: None
	)
	monkeypatch.setattr('compass.runner.write_current_repo_state', lambda target_path: tmp_path)
	monkeypatch.setattr('compass.runner._run_adapters', fake_run_adapters)

	result = asyncio.run(run(config))

	assert result == ['summary']
	assert calls == ['python']


def test_runner_propagates_collector_error(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config = CompassConfig(
		target_path=str(tmp_path),
		adapters=['rules'],
		provider='claude',
		lang='auto',
		reanalyze=True,
	)

	async def fake_check_prerequisites() -> None:
		return None

	async def fake_collect_analysis_context(
		passed_config: CompassConfig,
		language: str,
	) -> dict[str, object]:
		raise CollectorError('git_log', 'boom')

	monkeypatch.setattr('compass.runner._check_prerequisites', fake_check_prerequisites)
	monkeypatch.setattr(
		'compass.runner._detect_language', lambda passed_config, target_path: 'generic'
	)
	monkeypatch.setattr('compass.runner._collect_analysis_context', fake_collect_analysis_context)

	with pytest.raises(CollectorError, match='git_log'):
		asyncio.run(run(config))


def test_runner_propagates_adapter_error(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config = CompassConfig(
		target_path=str(tmp_path),
		adapters=['rules'],
		provider='claude',
		lang='auto',
		reanalyze=False,
	)
	(tmp_path / '.compass').mkdir()
	(tmp_path / '.compass' / 'analysis_context.json').write_text('{}', encoding='utf-8')

	async def fake_check_prerequisites() -> None:
		return None

	async def fake_run_adapters(
		passed_config: CompassConfig,
		passed_context: object,
		language: str,
	) -> list[str]:
		raise AdapterError('rules', 'boom')

	monkeypatch.setattr('compass.runner._check_prerequisites', fake_check_prerequisites)
	monkeypatch.setattr(
		'compass.runner._detect_language', lambda passed_config, target_path: 'generic'
	)
	monkeypatch.setattr('compass.runner.is_stale', lambda target_path: False)
	monkeypatch.setattr(
		'compass.runner.read_analysis_context', lambda target_path: _build_analysis_context()
	)
	monkeypatch.setattr('compass.runner._run_adapters', fake_run_adapters)

	with pytest.raises(AdapterError, match='rules'):
		asyncio.run(run(config))


def test_build_orchestrator_uses_explicit_constructor_contract() -> None:
	config = CompassConfig(
		target_path='/tmp/repo',
		adapters=['rules'],
		provider='claude',
		lang='auto',
		reanalyze=False,
	)

	class FakeOrchestrator:
		def __init__(self, *, config: CompassConfig, language: str) -> None:
			self.config = config
			self.language = language

	orchestrator = _build_orchestrator(FakeOrchestrator, config, 'python')

	assert orchestrator.config == config
	assert orchestrator.language == 'python'


def test_collect_analysis_context_uses_collector_run_with_target_path(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	config = CompassConfig(
		target_path=str(tmp_path),
		adapters=['rules'],
		provider='claude',
		lang='python',
		reanalyze=False,
	)
	calls: list[Path] = []
	expected = _build_analysis_context()

	class FakeCollectorOrchestrator:
		def __init__(self) -> None:
			pass

		async def run(self, target_path: Path) -> AnalysisContext:
			calls.append(target_path)
			return expected

	monkeypatch.setattr(
		'compass.runner._load_collector_orchestrator',
		lambda: FakeCollectorOrchestrator,
	)

	result = asyncio.run(_collect_analysis_context(config, 'python'))

	assert result == expected
	assert calls == [tmp_path]


def test_call_async_method_does_not_await_plain_awaitable_object() -> None:
	class PlainAwaitable:
		def __await__(self):  # type: ignore[no-untyped-def]
			async def _inner() -> str:
				return 'awaited'

			return _inner().__await__()

	class FakeInstance:
		def build(self) -> PlainAwaitable:
			return PlainAwaitable()

	result = asyncio.run(_call_async_method(FakeInstance(), 'build'))

	assert isinstance(result, PlainAwaitable)
