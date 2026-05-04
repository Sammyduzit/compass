from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from compass.errors import RepomixError
from compass.repomix import run_repomix


async def test_run_repomix_happy_path(tmp_path):
	mock_proc = AsyncMock()
	mock_proc.returncode = 0
	mock_proc.communicate = AsyncMock(return_value=(b'compressed output', b''))

	with patch('compass.repomix.asyncio.create_subprocess_exec', return_value=mock_proc):
		result = await run_repomix([str(tmp_path / 'file1.py')], repo_root=tmp_path)

	assert result == 'compressed output'


async def test_run_repomix_raises_on_failure(tmp_path):
	mock_proc = AsyncMock()
	mock_proc.returncode = 1
	mock_proc.communicate = AsyncMock(return_value=(b'', b'something went wrong'))

	with patch('compass.repomix.asyncio.create_subprocess_exec', return_value=mock_proc):
		with pytest.raises(RepomixError):
			await run_repomix([str(tmp_path / 'file1.py')], repo_root=tmp_path)


def test_run_repomix_raises_on_path_escape(tmp_path):
	outside = Path('/tmp/evil.py')
	with pytest.raises(RepomixError, match='path escapes repo root'):
		import asyncio

		asyncio.run(run_repomix([str(outside)], repo_root=tmp_path))
