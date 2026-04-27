from unittest.mock import MagicMock, patch
import pytest
from compass.repomix import run_repomix
from compass.errors import RepomixError


def test_run_repomix_happy_path():
	mock_result = MagicMock()
	mock_result.returncode = 0
	mock_result.stdout = 'compressed output'

	with patch('compass.repomix.subprocess.run', return_value=mock_result):
		result = run_repomix(['file1.py', 'file2.py'])

	assert result == 'compressed output'


def test_run_repomix_raises_on_failure():
	mock_result = MagicMock()
	mock_result.returncode = 1
	mock_result.stderr = 'something went wrong'

	with patch('compass.repomix.subprocess.run', return_value=mock_result):
		with pytest.raises(RepomixError):
			run_repomix(['file1.py'])
