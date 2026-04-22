import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.types import TextContent

from compass.collectors.import_graph import ImportGraphCollector
from compass.errors import CollectorError


def make_mcp_response(data: dict) -> MagicMock:
    content = TextContent(type='text', text=json.dumps(data))
    result = MagicMock()
    result.content = [content]
    return result


async def test_happy_path():
    centrality_output = {
    	'results': [
    		{'file_path': 'src/app.py', 'in_degree': 3},
    		{'file_path': 'src/config.py', 'in_degree': 1},
    	]
    }
    edges_output = {'results': [{'source': 'src/app.py', 'target': 'src/config.py'}]}

    mock_session = AsyncMock()
    mock_session.call_tool.side_effect = [
        make_mcp_response(centrality_output),
    	make_mcp_response(edges_output),
    ]

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=(None, None))
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    mock_client_session = MagicMock()
    mock_client_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_client_session.__aexit__ = AsyncMock(return_value=None)

    with patch('pathlib.Path.exists', return_value=True), \
        patch('compass.collectors.import_graph.stdio_client', return_value=mock_cm), \
        patch('compass.collectors.import_graph.ClientSession', return_value=mock_client_session):
        collector = ImportGraphCollector()
        result = await collector.collect(Path("/fake/repo"))

    assert result.centrality['src/app.py'] == 1.0
    assert result.centrality['src/config.py'] == pytest.approx(1/3)
    assert 'src/app.py' in result.cluster_id

async def test_failure_path():
    with patch('pathlib.Path.exists', return_value=False):
        collector = ImportGraphCollector()
        with pytest.raises(CollectorError):
            await collector.collect(Path("/fake/repo"))
