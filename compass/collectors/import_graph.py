import json
from dataclasses import dataclass
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

from compass.collectors.base import BaseCollector
from compass.domain.cluster import Cluster
from compass.errors import CollectorError


@dataclass
class ImportGraphResult:
	centrality: dict[str, float]
	cluster_id: dict[str, int]
	clusters: list[Cluster]


class ImportGraphCollector(BaseCollector[ImportGraphResult]):
	async def collect(self, target_path: Path) -> ImportGraphResult:
		mcp_binary_path = Path.home() / '.compass' / 'bin' / 'codebase-memory-mcp'

		if not mcp_binary_path.exists():
			raise CollectorError('ImportGraphCollector', f'{mcp_binary_path} does not exist.')

		server_params = StdioServerParameters(
			command=str(mcp_binary_path),
			args=[str(target_path)],
		)

		async with stdio_client(server_params) as (read, write):
			async with ClientSession(read, write) as session:
				await session.initialize()

				result = await session.call_tool(
					'search_graph',
					{
						'project': str(target_path),
						'label': 'File',
					},
				)

				if not result.content or not isinstance(result.content[0], TextContent):
					raise CollectorError(
						'ImportGraphCollector', 'unexpected response from codebase-memory-mcp'
					)

				data = json.loads(result.content[0].text)
				nodes = data.get('results', [])

				max_degree = max(
					(node['in_degree'] + node['out_degree'] for node in nodes), default=1
				)
