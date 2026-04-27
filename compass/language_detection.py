"""Language detection for target repositories."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Literal


DetectedLanguage = Literal['python', 'typescript', 'generic']

PYTHON_SUFFIXES = {'.py'}
TYPESCRIPT_SUFFIXES = {'.ts', '.tsx', '.js', '.jsx'}
IGNORED_DIRECTORIES = {
	'.compass',
	'.git',
	'.hg',
	'.mypy_cache',
	'.pytest_cache',
	'.ruff_cache',
	'.svn',
	'.tox',
	'.venv',
	'__pycache__',
	'build',
	'dist',
	'node_modules',
	'venv',
}
MIN_RELEVANT_FILES = 5
DOMINANCE_THRESHOLD = 0.6


def detect(target_path: str | Path, override: DetectedLanguage | str = 'auto') -> DetectedLanguage:
	"""Detect the primary language of a repository.

	Compass currently only distinguishes between Python, TypeScript/JavaScript,
	and a generic fallback.
	"""

	if override == 'python':
		return 'python'
	if override == 'typescript':
		return 'typescript'
	if override == 'generic':
		return 'generic'

	counts = _count_relevant_files(Path(target_path))
	total = sum(counts.values())
	if total < MIN_RELEVANT_FILES:
		return 'generic'

	python_ratio = counts['python'] / total
	typescript_ratio = counts['typescript'] / total

	if python_ratio >= DOMINANCE_THRESHOLD and counts['python'] > counts['typescript']:
		return 'python'
	if typescript_ratio >= DOMINANCE_THRESHOLD and counts['typescript'] > counts['python']:
		return 'typescript'
	return 'generic'


def _count_relevant_files(target_path: Path) -> Counter[str]:
	counts: Counter[str] = Counter()

	for file_path in target_path.rglob('*'):
		if not file_path.is_file():
			continue
		if _is_ignored(file_path, target_path):
			continue

		suffix = file_path.suffix.lower()
		if suffix in PYTHON_SUFFIXES:
			counts['python'] += 1
		elif suffix in TYPESCRIPT_SUFFIXES:
			counts['typescript'] += 1

	return counts


def _is_ignored(file_path: Path, target_path: Path) -> bool:
	try:
		relative_parts = file_path.relative_to(target_path).parts
	except ValueError:
		return False
	return any(part in IGNORED_DIRECTORIES for part in relative_parts[:-1])
