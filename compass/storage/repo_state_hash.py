"""Compute repository fingerprints for staleness checks."""

from __future__ import annotations

import subprocess  # nosec B404
from pathlib import Path
from shutil import which


def get_repo_head(target_path: str | Path) -> str:
	"""Return the current git HEAD SHA for ``target_path``."""

	git_bin = which('git')
	if git_bin is None:
		raise FileNotFoundError('git executable not found')

	result = subprocess.run(
		[git_bin, 'rev-parse', 'HEAD'],
		cwd=Path(target_path),
		check=True,
		capture_output=True,
		text=True,
	)  # nosec B603
	return result.stdout.strip()
