import json
import pytest
from unittest.mock import AsyncMock, patch
from compass.collectors.ast_grep import AstGrepCollector
from compass.errors import CollectorError


@pytest.mark.asyncio
async def test_ast_grep_collector_happy_path(tmp_path):
    fake_output = json.dumps([{"text": "except ValueError as e:"}]).encode()

    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(fake_output, b""))

    with patch(
        "compass.collectors.ast_grep.asyncio.create_subprocess_exec",
        return_value=mock_proc,
    ):
        collector = AstGrepCollector()
        result = await collector.collect(tmp_path)

    assert "except ValueError as e:" in result["error_handling"]


@pytest.mark.asyncio
async def test_ast_grep_collector_raises_on_failure(tmp_path):
    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate = AsyncMock(return_value=(b"", b"error"))

    with patch(
        "compass.collectors.ast_grep.asyncio.create_subprocess_exec",
        return_value=mock_proc,
    ):
        collector = AstGrepCollector()
        with pytest.raises(CollectorError):
            await collector.collect(tmp_path)
