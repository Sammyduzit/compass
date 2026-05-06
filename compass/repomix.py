import asyncio
from pathlib import Path

from compass.errors import RepomixError


async def run_repomix(paths: list[str], repo_root: Path) -> str:
	abs_root = repo_root.resolve()
	for p in paths:
		resolved = (abs_root / p).resolve() if not Path(p).is_absolute() else Path(p).resolve()
		if not resolved.is_relative_to(abs_root):
			raise RepomixError(f'path escapes repo root: {p}')

	proc = await asyncio.create_subprocess_exec(
		'repomix',
		str(abs_root),
		'--include',
		','.join(paths),
		'--compress',
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.PIPE,
	)
	stdout, stderr = await proc.communicate()
	if proc.returncode != 0:
		raise RepomixError(stderr.decode())

	return stdout.decode()
