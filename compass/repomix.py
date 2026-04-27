import subprocess  # nosec B404
from pathlib import Path

from compass.errors import RepomixError


def run_repomix(paths: list[str], repo_root: Path) -> str:
	for p in paths:
		if not Path(p).resolve().is_relative_to(repo_root.resolve()):
			raise RepomixError(f'path escapes repo root: {p}')

	result = subprocess.run(  # nosec B603 -- paths validated against repo_root
		['repomix', '--compress'] + paths,
		capture_output=True,
		text=True,
	)
	if result.returncode != 0:
		raise RepomixError(result.stderr)

	return result.stdout
