"""Unit tests for the Compass CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from compass.cli import build_config, main, parse_adapters
from compass.config import CompassConfig
from compass.errors import CompassError, ConfigError


def test_parse_adapters_expands_all_and_deduplicates() -> None:
	assert parse_adapters('all') == ['rules', 'summary']
	assert parse_adapters('rules,summary,rules') == ['rules', 'summary']


def test_parse_adapters_rejects_unknown_values() -> None:
	with pytest.raises(ConfigError, match='Invalid config value for'):
		parse_adapters('rules,unknown')


def test_build_config_merges_global_project_and_cli(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	home_dir = tmp_path / 'home'
	target_repo = tmp_path / 'repo'
	(home_dir / '.compass').mkdir(parents=True)
	(target_repo / '.compass').mkdir(parents=True)

	(home_dir / '.compass' / 'config.yaml').write_text(
		'default_provider: claude\nlang: python\n',
		encoding='utf-8',
	)
	(target_repo / '.compass' / 'config.yaml').write_text(
		'default_provider: codex\nlang: typescript\n',
		encoding='utf-8',
	)

	monkeypatch.setattr('compass.cli.Path.home', lambda: home_dir)

	args = argparse.Namespace(
		target_path=str(target_repo),
		adapters='all',
		provider='claude',
		lang=None,
		reanalyze=True,
	)

	assert build_config(args) == CompassConfig(
		target_path=str(target_repo),
		adapters=['rules', 'summary'],
		provider='claude',
		lang='typescript',
		reanalyze=True,
	)


def test_main_builds_config_and_calls_runner(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	captured: list[CompassConfig] = []
	home_dir = tmp_path / 'home'
	target_repo = tmp_path / 'repo'
	(home_dir / '.compass').mkdir(parents=True)
	target_repo.mkdir()

	(home_dir / '.compass' / 'config.yaml').write_text(
		'default_provider: codex\nlang: python\n',
		encoding='utf-8',
	)

	monkeypatch.setattr('compass.cli.Path.home', lambda: home_dir)
	monkeypatch.setattr('compass.cli._run_runner', lambda config: captured.append(config))

	exit_code = main([str(target_repo), '--adapters', 'rules'])

	assert exit_code == 0
	assert captured == [
		CompassConfig(
			target_path=str(target_repo),
			adapters=['rules'],
			provider='codex',
			lang='python',
			reanalyze=False,
		)
	]


def test_main_runs_end_to_end_with_mocked_pipeline(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	target_repo = tmp_path / 'repo'
	target_repo.mkdir()

	async def fake_check_prerequisites(target_path: Path) -> None:
		return None

	async def fake_collect_analysis_context(
		config: CompassConfig,
		language: str,
	) -> dict[str, object]:
		assert config.target_path == str(target_repo)
		assert language == 'python'
		return {'architecture': {'file_scores': []}}

	async def fake_run_adapters(
		config: CompassConfig,
		analysis_context: object,
		language: str,
	) -> list[object]:
		assert config.adapters == ['rules']
		assert analysis_context == {'architecture': {'file_scores': []}}
		assert language == 'python'
		return []

	monkeypatch.setattr('compass.runner._check_prerequisites', fake_check_prerequisites)
	monkeypatch.setattr('compass.runner._detect_language', lambda config, target_path: 'python')
	monkeypatch.setattr('compass.runner._should_run_phase_one', lambda config, target_path: True)
	monkeypatch.setattr('compass.runner._collect_analysis_context', fake_collect_analysis_context)
	monkeypatch.setattr('compass.runner._run_adapters', fake_run_adapters)
	monkeypatch.setattr(
		'compass.runner.write_analysis_context', lambda target_path, analysis_context: None
	)
	monkeypatch.setattr('compass.runner.write_current_repo_state', lambda target_path: None)

	assert main([str(target_repo), '--adapters', 'rules']) == 0


def test_main_returns_one_for_compass_errors(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
	capsys: pytest.CaptureFixture[str],
) -> None:
	target_repo = tmp_path / 'repo'
	target_repo.mkdir()

	monkeypatch.setattr(
		'compass.cli._run_runner',
		lambda config: (_ for _ in ()).throw(CompassError('runner failed')),
	)

	exit_code = main([str(target_repo)])

	assert exit_code == 1
	assert 'runner failed' in capsys.readouterr().err


def test_main_surfaces_invalid_arguments(capsys: pytest.CaptureFixture[str]) -> None:
	with pytest.raises(SystemExit) as error:
		main(['repo', '--provider', 'invalid'])

	assert error.value.code == 2
	assert 'invalid choice' in capsys.readouterr().err
