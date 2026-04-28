from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from compass.adapters.base import AdapterBase
from compass.config import CompassConfig
from compass.errors import ProviderError, SchemaValidationError
from compass.paths import compass_paths


class _TestAdapter(AdapterBase):
	name = 'test'

	async def run(self) -> None:
		pass


def _config(provider: str = 'claude') -> CompassConfig:
	return CompassConfig(target_path='/tmp/repo', adapters=['test'], provider=provider)


@pytest.fixture
def adapter(tmp_path):
	config = _config()
	with patch('compass.adapters.base.get_provider') as mock_get:
		mock_provider = MagicMock()
		mock_provider.call = AsyncMock(return_value='provider response')
		mock_get.return_value = mock_provider
		inst = _TestAdapter(config, compass_paths(tmp_path))
		inst._provider = mock_provider
		return inst


# --- run_file_selector ---


def test_run_file_selector_returns_empty_list(adapter):
	result = adapter.run_file_selector({'type': 'high_centrality'})
	assert result == []


# --- call_provider ---


async def test_call_provider_returns_response(adapter):
	adapter._provider.call = AsyncMock(return_value='LLM output')
	result = await adapter.call_provider('my prompt')
	assert result == 'LLM output'


async def test_call_provider_wraps_runtime_error_as_provider_error(adapter):
	adapter._provider.call = AsyncMock(side_effect=RuntimeError('timed out'))
	with pytest.raises(ProviderError):
		await adapter.call_provider('my prompt')


# --- validate_output ---


async def test_validate_output_returns_result_when_valid(adapter):
	validator = MagicMock(return_value='parsed')
	adapter.call_provider = AsyncMock(return_value='raw response')
	result = await adapter.validate_output('raw response', validator, 'original prompt')
	assert result == 'parsed'
	validator.assert_called_once_with('raw response')


async def test_validate_output_retries_once_on_validation_failure(adapter):
	call_count = 0

	def validator(raw: str) -> str:
		nonlocal call_count
		call_count += 1
		if call_count == 1:
			raise ValueError('missing required section')
		return 'parsed on retry'

	adapter.call_provider = AsyncMock(return_value='retry response')

	with patch('asyncio.sleep', new_callable=AsyncMock):
		result = await adapter.validate_output('bad response', validator, 'original prompt')

	assert result == 'parsed on retry'
	assert call_count == 2
	adapter.call_provider.assert_called_once()
	call_args = adapter.call_provider.call_args[0][0]
	assert 'original prompt' in call_args
	assert 'missing required section' in call_args


async def test_validate_output_raises_schema_error_after_second_failure(adapter):
	def validator(raw: str) -> str:
		raise ValueError('still invalid')

	adapter.call_provider = AsyncMock(return_value='retry response')

	with patch('asyncio.sleep', new_callable=AsyncMock):
		with pytest.raises(SchemaValidationError):
			await adapter.validate_output('bad response', validator, 'original prompt')


async def test_validate_output_does_not_call_provider_when_first_attempt_succeeds(adapter):
	validator = MagicMock(return_value='parsed')
	adapter.call_provider = AsyncMock()

	await adapter.validate_output('good response', validator, 'original prompt')

	adapter.call_provider.assert_not_called()


# --- run_grep_ast ---


async def test_run_grep_ast_returns_stdout_from_subprocess(adapter, tmp_path):
	fake_file = tmp_path / 'module.py'
	fake_file.write_text('def foo(): pass')

	mock_proc = MagicMock()
	mock_proc.returncode = 0
	mock_proc.communicate = AsyncMock(return_value=(b'def foo(): pass\n', b''))

	with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
		mock_exec.return_value = mock_proc
		result = await adapter.run_grep_ast([str(fake_file)])

	assert 'def foo' in result


async def test_run_grep_ast_returns_empty_string_for_no_files(adapter):
	result = await adapter.run_grep_ast([])
	assert result == ''
