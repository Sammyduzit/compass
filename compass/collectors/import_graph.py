import json
from dataclasses import dataclass
from pathlib import Path

import networkx as nx

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

				project_name = await _get_or_index_project(session, target_path)

				# centrality: in-degree per file
				centrality_result = await session.call_tool(
					'query_graph',
					{
						'project': project_name,
						'query': """
							MATCH (importer:File)-[]->(imported:File)
							RETURN imported.file_path AS file_path, COUNT(importer) AS in_degree
							ORDER BY in_degree DESC
						""",
					},
				)
				if not centrality_result.content or not isinstance(
					centrality_result.content[0], TextContent
				):
					raise CollectorError(
						'ImportGraphCollector',
						'unexpected response from codebase-memory-mcp (centrality)',
					)

				rows = _parse_rows(json.loads(centrality_result.content[0].text))
				max_degree = max((int(row['in_degree']) for row in rows), default=1)
				centrality = {row['file_path']: int(row['in_degree']) / max_degree for row in rows}

				# clusters: connected components via louvain on import edges
				edge_result = await session.call_tool(
					'query_graph',
					{
						'project': project_name,
						'query': """
							MATCH (a:File)-[]->(b:File)
							RETURN a.file_path AS source, b.file_path AS target
						""",
					},
				)
				if not edge_result.content or not isinstance(edge_result.content[0], TextContent):
					raise CollectorError(
						'ImportGraphCollector',
						'unexpected response from codebase-memory-mcp (edges)',
					)

				edge_rows = _parse_rows(json.loads(edge_result.content[0].text))

				G: nx.Graph = nx.Graph()
				for row in edge_rows:
					G.add_edge(row['source'], row['target'])

				communities = (
					nx.algorithms.community.louvain_communities(G, seed=0)
					if G.number_of_nodes() > 0
					else []
				)

				cluster_id: dict[str, int] = {}
				clusters = []
				for cid, community in enumerate(communities):
					for node in community:
						cluster_id[node] = cid
					clusters.append(Cluster(id=cid, files=tuple(community)))

				return ImportGraphResult(
					centrality=centrality,
					cluster_id=cluster_id,
					clusters=clusters,
				)


async def _get_or_index_project(session: ClientSession, target_path: Path) -> str:
	resolved = str(target_path.resolve())

	projects_result = await session.call_tool('list_projects', {})
	if isinstance(projects_result.content[0], TextContent):
		projects = json.loads(projects_result.content[0].text).get('projects', [])
		for p in projects:
			if p.get('root_path') == resolved:
				return p['name']

	index_result = await session.call_tool(
		'index_repository',
		{'repo_path': str(target_path)},
	)
	if isinstance(index_result.content[0], TextContent):
		data = json.loads(index_result.content[0].text)
		project_name = data.get('project')
		if project_name:
			return project_name

	raise CollectorError('ImportGraphCollector', 'failed to get project name from codebase-memory-mcp')


def _parse_rows(data: dict) -> list[dict]:
	columns = data.get('columns', [])
	rows = data.get('rows', [])
	return [dict(zip(columns, row)) for row in rows]
