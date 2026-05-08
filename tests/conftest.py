"""Shared pytest configuration for Compass tests."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures'
FIXTURE_SCRIPT = FIXTURES_DIR / 'setup.sh'
_FIXTURE_CACHE: dict[str, Path] = {}


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


def _resolve_bash() -> str:
	if os.name != 'nt':
		return 'bash'

	found = shutil.which('bash')
	if found and 'system32\\bash.exe' not in found.lower():
		return found

	candidates: list[Path] = []
	for root in (os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)')):
		if not root:
			continue

		candidates.extend(
			[
				Path(root) / 'Git' / 'usr' / 'bin' / 'bash.exe',
				Path(root) / 'Git' / 'bin' / 'bash.exe',
			]
		)

	for candidate in candidates:
		if candidate.is_file():
			return str(candidate)

	raise FileNotFoundError('Git Bash not found on Windows runner')


def _has_worktree_entries(repo_path: Path) -> bool:
	return any(entry.name != '.git' for entry in repo_path.iterdir())


def _is_valid_fixture_repo(repo_path: Path) -> bool:
	if not repo_path.is_dir() or not (repo_path / '.git').is_dir():
		return False
	if not _has_worktree_entries(repo_path):
		return False
	result = subprocess.run(
		['git', '-C', str(repo_path), 'rev-parse', '--verify', 'HEAD'],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	)
	return result.returncode == 0


def _remove_fixture_repo(repo_path: Path) -> None:
	if not repo_path.exists():
		return
	if sys.platform == 'darwin':
		subprocess.run(
			['chflags', '-R', 'nouchg,noschg', str(repo_path)],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)

	def _onerror(func, path: str, _exc_info) -> None:
		try:
			os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
		except OSError:
			return
		try:
			func(path)
		except OSError:
			return

	shutil.rmtree(repo_path, onerror=_onerror)


def setup_fixture_repo(name: str) -> Path:
	"""Recreate a synthetic fixture repository and return its path."""

	repo_path = _FIXTURE_CACHE.get(name) or (FIXTURES_DIR / name)
	if _is_valid_fixture_repo(repo_path):
		_FIXTURE_CACHE[name] = repo_path
		return repo_path
	if repo_path.exists():
		_remove_fixture_repo(repo_path)

	try:
		bash_path = _resolve_bash()
	except FileNotFoundError:
		pytest.skip('Skipping integration fixtures: Git Bash not available on Windows')

	subprocess.run(
		[bash_path, str(FIXTURE_SCRIPT), name],
		check=True,
		cwd=FIXTURES_DIR.parent.parent,
	)
	if not repo_path.is_dir():
		raise RuntimeError(f'Fixture repo was not created: {repo_path}')
	_FIXTURE_CACHE[name] = repo_path
	return repo_path


@pytest.fixture
def fixture_repo_factory() -> Callable[[str], Path]:
	"""Factory fixture that recreates and returns named fixture repositories."""

	return setup_fixture_repo
