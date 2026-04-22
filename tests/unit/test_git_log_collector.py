from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from compass.collectors.git_log import GitLogCollector
from compass.errors import CollectorError


async def test_happy_path():
	commits_output = 'COMMIT abc123\nsrc/app.py\nsrc/config.py\n\nCOMMIT def456\nsrc/app.py'
	timestamps_output = (
		'COMMIT 1700000000\nsrc/app.py\nsrc/config.py\n\nCOMMIT 1699000000\nsrc/app.py'
	)

	def make_proc(stdout: str):
		proc = AsyncMock()
		proc.returncode = 0
		proc.communicate.return_value = (stdout.encode(), b'')
		return proc

	with patch(
		'compass.collectors.git_log.asyncio.create_subprocess_exec',
		side_effect=[make_proc(commits_output), make_proc(timestamps_output)],
	):
		collector = GitLogCollector()
		result = await collector.collect(Path('/fake/repo'))

		assert result.file_data['src/app.py'].churn == 1.0
		assert result.file_data['src/config.py'].churn == 0.5
		assert 'src/config.py' in result.file_data['src/app.py'].coupling_pairs
		assert (
			result.file_data['src/app.py'].age >= 0
		)  # Exact value us relative to "now", so only checks for positive integer


async def test_failure_path():

	mock_proc = AsyncMock()
	mock_proc.returncode = 1
	mock_proc.communicate = AsyncMock(return_value=(b'', b'error'))
	with patch(
		'compass.collectors.git_log.asyncio.create_subprocess_exec',
		return_value=mock_proc,
	):
		collector = GitLogCollector()
		with pytest.raises(CollectorError):
			await collector.collect(Path('/fake/repo'))
