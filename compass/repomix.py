import asyncio
from pathlib import Path
from compass.errors import RepomixError


async def run_repomix(paths: list[str], repo_root: Path) -> str:
    for p in paths:
        if not Path(p).resolve().is_relative_to(repo_root.resolve()):
            raise RepomixError(f'path escapes repo root: {p}')

    proc = await asyncio.create_subprocess_exec(  # nosec B603
        'repomix', '--compress', *paths,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RepomixError(stderr.decode())

    return stdout.decode()
