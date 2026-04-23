import asyncio
from pathlib import Path

from compass.collectors.ast_grep import AstGrepCollector
from compass.collectors.docs_reader import DocsReaderCollector
from compass.collectors.git_log import GitLogCollector
from compass.collectors.import_graph import ImportGraphCollector
from compass.domain.analysis_context import AnalysisContext
from compass.domain.architecture_snapshot import ArchitectureSnapshot
from compass.domain.cluster import Cluster
from compass.domain.file_score import FileScore
from compass.storage.analysis_context_store import AnalysisContextStore  # type: ignore[import-not-found]  # storage module not yet merged


class CollectorOrchestrator:
	def __init__(self) -> None:
		self._git_log = GitLogCollector()
		self._ast_grep = AstGrepCollector()
		self._docs_reader = DocsReaderCollector()
		self._import_graph = ImportGraphCollector()

	async def run(self, target_path: Path) -> AnalysisContext:
		git_result, patterns, docs = await asyncio.gather(
			self._git_log.collect(target_path),
			self._ast_grep.collect(target_path),
			self._docs_reader.collect(target_path),
		)

		import_graph_result = await self._import_graph.collect(target_path)
		centrality_by_file = import_graph_result.centrality  # dict[str, float]
		clusters = import_graph_result.clusters  # list[Cluster]

		file_scores = [
			FileScore(
				path=file_path,
				churn=data.churn,
				age=data.age,
				centrality=centrality_by_file.get(file_path, 0.0),
				cluster_id=_find_cluster_id(file_path, clusters),
				coupling_pairs=tuple(data.coupling_pairs),
			)
			for file_path, data in git_result.file_data.items()
		]
		architecture = ArchitectureSnapshot(
			file_scores=file_scores,
			coupling_pairs=git_result.coupling_pairs,
			clusters=clusters,
		)

		context = AnalysisContext(
			architecture=architecture,
			patterns=patterns,
			git_patterns=git_result.git_patterns,
			docs=docs,
		)

		await AnalysisContextStore().write(target_path, context)

		return context


def _find_cluster_id(file_path: str, clusters: list[Cluster]) -> int:
	for cluster in clusters:
		if file_path in cluster.files:
			return cluster.id
	return -1
