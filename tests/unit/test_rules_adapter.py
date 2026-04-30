from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from compass.adapters.rules import RulesAdapter
from compass.config import CompassConfig
from compass.paths import compass_paths


def _config() -> CompassConfig:
    return CompassConfig(target_path='/tmp/repo', adapters=['rules'], provider='claude')


@pytest.fixture
def adapter(tmp_path):
    config = _config()
    with patch('compass.adapters.base.get_provider') as mock_get:
        mock_provider = MagicMock()
        mock_provider.call = AsyncMock(return_value='provider response')
        mock_get.return_value = mock_provider
        inst = RulesAdapter(config, compass_paths(tmp_path))
        inst._provider = mock_provider
        return inst


# --- parse_reconciliation_output ---


def test_parse_reconciliation_output_success(adapter):
    valid_llm_response = """
    Some analysis text from the LLM.

    ### FINAL YAML OUTPUT ###
    ```yaml
    clusters:
      typing:
        - "Always use explicit types"
    ```
    """

    result = adapter.parse_reconciliation_output(valid_llm_response)

    assert "clusters:" in result
    assert "Always use explicit types" in result


def test_parse_reconciliation_output_raises_on_missing_header(adapter):
    invalid_llm_response = """
    Here is the yaml you asked for:
    ```yaml
    clusters:
      typing: []
    ```
    """

    with pytest.raises(ValueError, match="missing strict section header"):
        adapter.parse_reconciliation_output(invalid_llm_response)
