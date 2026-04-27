import subprocess
from compass.errors import RepomixError


def run_repomix(paths: list[str]) -> str:
	result = subprocess.run(['repomix', '--compress'] + paths, capture_output=True, text=True)
	if result.returncode != 0:
		raise RepomixError(result.stderr)

	return result.stdout
