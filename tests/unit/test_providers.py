from __future__ import annotations

import pytest

from compass.config import CompassConfig
from compass.errors import ConfigError
from compass.providers.base import get_provider
from compass.providers.claude import ClaudeProvider
from compass.providers.codex import CodexProvider


def _config(provider: str | None) -> CompassConfig:
	return CompassConfig(target_path='/tmp/repo', adapters=['rules'], provider=provider)


def test_get_provider_returns_claude_provider():
	provider = get_provider(_config('claude'))
	assert isinstance(provider, ClaudeProvider)


def test_get_provider_returns_codex_provider():
	provider = get_provider(_config('codex'))
	assert isinstance(provider, CodexProvider)


def test_get_provider_raises_config_error_on_none():
	with pytest.raises(ConfigError):
		get_provider(_config(None))


def test_get_provider_raises_config_error_on_unknown():
	with pytest.raises(ConfigError):
		get_provider(_config('gpt4'))
