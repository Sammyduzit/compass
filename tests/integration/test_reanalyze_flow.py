from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from compass.config import CompassConfig
from compass.paths import compass_paths
from compass.runner import run
from tests.integration.conftest import commit_fixture_change

pytestmark = pytest.mark.integration


def _config(repo_path: Path, *, reanalyze: bool = False) -> CompassConfig:
	return CompassConfig(
		target_path=str(repo_path),
		adapters=[],
		provider=None,
		lang='auto',
		reanalyze=reanalyze,
	)


def test_reanalyze_flow_respects_staleness_and_force_flag(
	integration_repo,
	sample_analysis_context,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	repo_path = integration_repo('sample_repo_minimal')
	collect_calls: list[str] = []

	async def fake_check_prerequisites() -> None:
		return None

	async def fake_collect_analysis_context(
		config: CompassConfig,
		language: str,
	):
		collect_calls.append(language)
		return sample_analysis_context

	async def fake_run_adapters(
		config: CompassConfig,
		analysis_context,
		language: str,
	) -> list[object]:
		return []

	monkeypatch.setattr('compass.runner._check_prerequisites', fake_check_prerequisites)
	monkeypatch.setattr('compass.runner._collect_analysis_context', fake_collect_analysis_context)
	monkeypatch.setattr('compass.runner._run_adapters', fake_run_adapters)

	asyncio.run(run(_config(repo_path)))
	paths = compass_paths(repo_path)
	assert paths.analysis_context.exists()
	assert paths.repo_state.exists()
	assert collect_calls == ['generic']

	asyncio.run(run(_config(repo_path)))
	assert collect_calls == ['generic']

	commit_fixture_change(
		repo_path,
		'notes.txt',
		'first note\nsecond note\n',
		'test: update minimal fixture history',
	)
	asyncio.run(run(_config(repo_path)))
	assert collect_calls == ['generic', 'generic']

	asyncio.run(run(_config(repo_path, reanalyze=True)))
	assert collect_calls == ['generic', 'generic', 'generic']
