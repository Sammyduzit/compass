from __future__ import annotations

from importlib.util import find_spec

import pytest

pytestmark = pytest.mark.integration


def _summary_adapter_available() -> bool:
	return find_spec('compass.adapters.summary') is not None


@pytest.mark.skipif(
	not _summary_adapter_available(),
	reason='SummaryAdapter is not available yet; finalize assertions after issue #31 merges.',
)
def test_run_summary_pipeline_on_python_fixture() -> None:
	raise NotImplementedError('Finalize SummaryAdapter integration assertions after issue #31.')


@pytest.mark.skipif(
	not _summary_adapter_available(),
	reason='SummaryAdapter is not available yet; finalize assertions after issue #31 merges.',
)
def test_run_summary_pipeline_on_typescript_fixture() -> None:
	raise NotImplementedError('Finalize SummaryAdapter integration assertions after issue #31.')
