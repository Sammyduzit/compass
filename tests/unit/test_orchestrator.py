from unittest.mock import AsyncMock, patch

import pytest

from compass.collectors.git_log import FileGitData, GitLogResult
from compass.collectors.import_graph import ImportGraphResult
from compass.collectors.orchestrator import CollectorOrchestrator
from compass.domain.analysis_context import AnalysisContext
from compass.domain.cluster import Cluster
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot
from compass.errors import CollectorError


def build_git_result() -> GitLogResult:
	return GitLogResult(
		file_data={'main.py': FileGitData(churn=0.8, age=10, coupling_pairs=['utils.py'])},
		coupling_pairs=[],
		git_patterns=GitPatternsSnapshot(
			hotspots=['main.py'],
			stable_files=[],
			coupling_clusters=[],
		),
	)


def build_import_graph_result() -> ImportGraphResult:
	return ImportGraphResult(
		centrality={'main.py': 0.5},
		cluster_id={'main.py': 0},
		clusters=[Cluster(id=0, files=('main.py',))],
	)


async def test_orchestrator_happy_path(tmp_path):
	git_result = build_git_result()
	import_graph_result = build_import_graph_result()

	with (
		patch('compass.collectors.orchestrator.GitLogCollector') as MockGit,
		patch('compass.collectors.orchestrator.AstGrepCollector') as MockAst,
		patch('compass.collectors.orchestrator.DocsReaderCollector') as MockDocs,
		patch('compass.collectors.orchestrator.ImportGraphCollector') as MockImport,
	):
		MockGit.return_value.collect = AsyncMock(return_value=git_result)
		MockAst.return_value.collect = AsyncMock(
			return_value={'error_handling': ['except ValueError']}
		)
		MockDocs.return_value.collect = AsyncMock(return_value={'README.md': 'hello'})
		MockImport.return_value.collect = AsyncMock(return_value=import_graph_result)

		orchestrator = CollectorOrchestrator()
		result = await orchestrator.run(tmp_path)

	assert isinstance(result, AnalysisContext)


async def test_orchestrator_aborts_on_collector_failure(tmp_path):
	import_graph_result = build_import_graph_result()

	with (
		patch('compass.collectors.orchestrator.GitLogCollector') as MockGit,
		patch('compass.collectors.orchestrator.AstGrepCollector') as MockAst,
		patch('compass.collectors.orchestrator.DocsReaderCollector') as MockDocs,
		patch('compass.collectors.orchestrator.ImportGraphCollector') as MockImport,
	):
		MockGit.return_value.collect = AsyncMock(
			side_effect=CollectorError('GitLogCollector', 'git failed')
		)
		MockAst.return_value.collect = AsyncMock(return_value={'error_handling': []})
		MockDocs.return_value.collect = AsyncMock(return_value={})
		MockImport.return_value.collect = AsyncMock(return_value=import_graph_result)

		orchestrator = CollectorOrchestrator()
		with pytest.raises(CollectorError):
			await orchestrator.run(tmp_path)
