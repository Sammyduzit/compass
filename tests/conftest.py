"""Shared pytest configuration for Compass tests."""

from __future__ import annotations

from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
	parser.addoption(
		'--run-integration',
		action='store_true',
		default=False,
		help='Run integration tests in addition to unit tests.',
	)


def pytest_configure(config: pytest.Config) -> None:
	config.addinivalue_line(
		'markers',
		'integration: marks tests as integration',
	)


def pytest_cmdline_main(config: pytest.Config) -> int | None:
	if not config.getoption('--run-integration'):
		return None

	ignores = getattr(config.option, 'ignore', None)
	if ignores is None:
		return None

	config.option.ignore = [
		ignore for ignore in ignores if Path(str(ignore)) != Path('tests/integration')
	]
	return None


def pytest_ignore_collect(
	collection_path: Path,
	config: pytest.Config,
) -> bool | None:
	if config.getoption('--run-integration'):
		return None
	integration_dir = Path(str(config.rootpath)) / 'tests' / 'integration'
	try:
		collection_path.relative_to(integration_dir)
	except ValueError:
		return None
	return True


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
	if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
		session.exitstatus = pytest.ExitCode.OK
