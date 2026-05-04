"""Unit tests for repository language detection."""

from __future__ import annotations

from pathlib import Path

from compass.language_detection import detect


FIXTURES_DIR = Path(__file__).resolve().parents[1] / 'fixtures'


def test_detect_returns_python_for_python_fixture() -> None:
	assert detect(FIXTURES_DIR / 'sample_repo_python') == 'python'


def test_detect_returns_typescript_for_typescript_fixture() -> None:
	assert detect(FIXTURES_DIR / 'sample_repo_typescript') == 'typescript'


def test_detect_returns_generic_for_minimal_fixture() -> None:
	assert detect(FIXTURES_DIR / 'sample_repo_minimal') == 'generic'


def test_detect_respects_override() -> None:
	assert detect(FIXTURES_DIR / 'sample_repo_typescript', override='python') == 'python'


def test_detect_ignores_internal_directories(tmp_path: Path) -> None:
	(tmp_path / '.git').mkdir()
	(tmp_path / '.git' / 'ignored.py').write_text('print("ignored")\n', encoding='utf-8')
	(tmp_path / 'src').mkdir()
	(tmp_path / 'src' / 'app.ts').write_text('export const app = 1;\n', encoding='utf-8')
	(tmp_path / 'src' / 'service.ts').write_text('export const service = 1;\n', encoding='utf-8')
	(tmp_path / 'src' / 'cache.ts').write_text('export const cache = 1;\n', encoding='utf-8')
	(tmp_path / 'src' / 'events.ts').write_text('export const events = 1;\n', encoding='utf-8')
	(tmp_path / 'src' / 'utils.ts').write_text('export const utils = 1;\n', encoding='utf-8')

	assert detect(tmp_path) == 'typescript'


def test_detect_returns_generic_for_mixed_repo_without_clear_majority(tmp_path: Path) -> None:
	for filename in ('a.py', 'b.py', 'c.py'):
		(tmp_path / filename).write_text('print("x")\n', encoding='utf-8')
	for filename in ('a.ts', 'b.ts', 'c.ts'):
		(tmp_path / filename).write_text('export const x = 1;\n', encoding='utf-8')

	assert detect(tmp_path) == 'generic'
