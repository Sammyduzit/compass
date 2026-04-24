from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from compass.config import CompassConfig, PROVIDER_TIMEOUT
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


def _make_proc(returncode: int, stdout: bytes, stderr: bytes) -> MagicMock:
	proc = MagicMock()
	proc.returncode = returncode
	proc.communicate = AsyncMock(return_value=(stdout, stderr))
	proc.kill = MagicMock()
	proc.wait = AsyncMock()
	return proc


async def test_claude_returns_stdout_on_success():
	proc = _make_proc(0, b'  extracted rules  ', b'')
	with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
		mock_exec.return_value = proc
		provider = ClaudeProvider()
		result = await provider.call('my prompt')

	assert result == 'extracted rules'
	mock_exec.assert_called_once_with(
		'claude',
		'-p',
		'my prompt',
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.PIPE,
	)


async def test_claude_raises_runtime_error_on_nonzero_exit():
	proc = _make_proc(1, b'', b'rate limit hit')
	with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
		mock_exec.return_value = proc
		provider = ClaudeProvider()
		with pytest.raises(RuntimeError, match='rate limit hit'):
			await provider.call('my prompt')


async def test_claude_raises_runtime_error_on_timeout():
	proc = MagicMock()
	proc.kill = MagicMock()
	proc.wait = AsyncMock()
	proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
	with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
		mock_exec.return_value = proc
		provider = ClaudeProvider()
		with pytest.raises(RuntimeError, match=f'{PROVIDER_TIMEOUT}s'):
			await provider.call('my prompt')
	proc.kill.assert_called_once()


async def test_codex_returns_stdout_on_success():
	proc = _make_proc(0, b'  codex output  ', b'')
	with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
		mock_exec.return_value = proc
		provider = CodexProvider()
		result = await provider.call('my prompt')

	assert result == 'codex output'
	mock_exec.assert_called_once_with(
		'codex', 'exec', '-p', 'my prompt',
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.PIPE,
	)


async def test_codex_raises_runtime_error_on_nonzero_exit():
	proc = _make_proc(1, b'', b'quota exceeded')
	with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
		mock_exec.return_value = proc
		provider = CodexProvider()
		with pytest.raises(RuntimeError, match='quota exceeded'):
			await provider.call('my prompt')


async def test_codex_raises_runtime_error_on_timeout():
	proc = MagicMock()
	proc.kill = MagicMock()
	proc.wait = AsyncMock()
	proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
	with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
		mock_exec.return_value = proc
		provider = CodexProvider()
		with pytest.raises(RuntimeError, match=f'{PROVIDER_TIMEOUT}s'):
			await provider.call('my prompt')
	proc.kill.assert_called_once()
