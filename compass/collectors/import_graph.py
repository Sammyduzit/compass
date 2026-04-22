import json
from collections import defaultdict
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

				# centrality: in-degree per file
				centrality_result = await session.call_tool(
					'query_graph',
					{
						'query': '''
							MATCH (importer:File)-[:IMPORTS]->(imported:File)
							RETURN imported.file_path AS file_path, COUNT(importer) AS in_degree
							ORDER BY in_degree DESC
						''',
					},
				)
				if not centrality_result.content or not isinstance(
					centrality_result.content[0], TextContent
				):
					raise CollectorError(
						'ImportGraphCollector',
						'unexpected response from codebase-memory-mcp (centrality)',
					)

				rows = json.loads(centrality_result.content[0].text).get('results', [])
				max_degree = max((row['in_degree'] for row in rows), default=1)
				centrality = {
					row['file_path']: row['in_degree'] / max_degree
					for row in rows
				}

				# clusters: connected components via union-find on import edges
				edge_result = await session.call_tool(
					'query_graph',
					{
						'query': '''
							MATCH (a:File)-[:IMPORTS]->(b:File)
							RETURN a.file_path AS source, b.file_path AS target
						''',
					},
				)
				if not edge_result.content or not isinstance(
					edge_result.content[0], TextContent
				):
					raise CollectorError(
						'ImportGraphCollector',
						'unexpected response from codebase-memory-mcp (edges)',
					)

				edge_rows = json.loads(edge_result.content[0].text).get('results', [])

				parent: dict[str, str] = {}

				def find(x: str) -> str:
					parent.setdefault(x, x)
					if parent[x] != x:
						parent[x] = find(parent[x])
					return parent[x]

				def union(x: str, y: str) -> None:
					parent[find(x)] = find(y)

				for row in edge_rows:
					union(row['source'], row['target'])

				root_to_id: dict[str, int] = {}
				cluster_id: dict[str, int] = {}
				for path in parent:
					root = find(path)
					if root not in root_to_id:
						root_to_id[root] = len(root_to_id)
					cluster_id[path] = root_to_id[root]

				cluster_files: dict[int, list[str]] = defaultdict(list)
				for path, cid in cluster_id.items():
					cluster_files[cid].append(path)

				clusters = [
					Cluster(id=cid, files=tuple(files))
					for cid, files in cluster_files.items()
				]

				return ImportGraphResult(
					centrality=centrality,
					cluster_id=cluster_id,
					clusters=clusters,
				)
