from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from compass.errors import RepomixError
from compass.repomix import run_repomix


def test_run_repomix_happy_path(tmp_path):
	mock_result = MagicMock()
	mock_result.returncode = 0
	mock_result.stdout = 'compressed output'

	with patch('compass.repomix.subprocess.run', return_value=mock_result):
		result = run_repomix([str(tmp_path / 'file1.py')], repo_root=tmp_path)

	assert result == 'compressed output'


def test_run_repomix_raises_on_failure(tmp_path):
	mock_result = MagicMock()
	mock_result.returncode = 1
	mock_result.stderr = 'something went wrong'

	with patch('compass.repomix.subprocess.run', return_value=mock_result):
		with pytest.raises(RepomixError):
			run_repomix([str(tmp_path / 'file1.py')], repo_root=tmp_path)


def test_run_repomix_raises_on_path_escape(tmp_path):
	outside = Path('/tmp/evil.py')
	with pytest.raises(RepomixError, match='path escapes repo root'):
		run_repomix([str(outside)], repo_root=tmp_path)
