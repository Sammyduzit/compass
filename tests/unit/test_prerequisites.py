from unittest.mock import patch

import pytest

from compass.errors import PrerequisiteError
from compass.prerequisites import check


def test_check_passes_when_repomix_found():
	with patch('compass.prerequisites.shutil.which', return_value='/usr/local/bin/repomix'):
		check()


def test_check_raises_when_repomix_missing():
	with patch('compass.prerequisites.shutil.which', return_value=None):
		with pytest.raises(PrerequisiteError):
			check()
