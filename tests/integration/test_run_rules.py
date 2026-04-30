from __future__ import annotations

from importlib.util import find_spec

import pytest

pytestmark = pytest.mark.integration


def _rules_adapter_available() -> bool:
	return find_spec('compass.adapters.rules') is not None


@pytest.mark.skipif(
	not _rules_adapter_available(),
	reason='RulesAdapter is not available yet; finalize assertions after issue #30 merges.',
)
def test_run_rules_pipeline_on_python_fixture() -> None:
	raise NotImplementedError('Finalize RulesAdapter integration assertions after issue #30.')


@pytest.mark.skipif(
	not _rules_adapter_available(),
	reason='RulesAdapter is not available yet; finalize assertions after issue #30 merges.',
)
def test_run_rules_pipeline_on_typescript_fixture() -> None:
	raise NotImplementedError('Finalize RulesAdapter integration assertions after issue #30.')
