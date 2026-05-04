"""Shared pytest configuration for Compass tests."""

from __future__ import annotations

from pathlib import Path
import subprocess
from collections.abc import Callable

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures'
FIXTURE_SCRIPT = FIXTURES_DIR / 'setup.sh'


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
	if not _should_collect_integration(config):
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
	if _should_collect_integration(config):
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


def _should_collect_integration(config: pytest.Config) -> bool:
	if config.getoption('--run-integration'):
		return True
	markexpr = getattr(config.option, 'markexpr', '') or ''
	return 'integration' in markexpr


def fixture_root() -> Path:
	"""Return the root directory that contains synthetic test repositories."""

	return FIXTURES_DIR


def setup_fixture_repo(name: str) -> Path:
	"""Recreate a synthetic fixture repository and return its path."""

	subprocess.run(
		['bash', str(FIXTURE_SCRIPT), name],
		check=True,
		cwd=FIXTURES_DIR.parent.parent,
	)
	repo_path = FIXTURES_DIR / name
	if not repo_path.is_dir():
		raise RuntimeError(f'Fixture repo was not created: {repo_path}')
	return repo_path


@pytest.fixture
def fixture_repo_factory() -> Callable[[str], Path]:
	"""Factory fixture that recreates and returns named fixture repositories."""

	return setup_fixture_repo
