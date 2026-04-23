import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.modules.setdefault('compass.storage', MagicMock())
sys.modules.setdefault('compass.storage.analysis_context_store', MagicMock())

import pytest  # noqa: E402

from compass.collectors.git_log import FileGitData, GitLogResult  # noqa: E402
from compass.collectors.import_graph import ImportGraphResult  # noqa: E402
from compass.collectors.orchestrator import CollectorOrchestrator  # noqa: E402
from compass.domain.analysis_context import AnalysisContext  # noqa: E402
from compass.domain.cluster import Cluster  # noqa: E402
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot  # noqa: E402
from compass.errors import CollectorError  # noqa: E402


@pytest.fixture
def fake_git_result():
	return GitLogResult(
		file_data={'main.py': FileGitData(churn=0.8, age=10, coupling_pairs=['utils.py'])},
		coupling_pairs=[],
		git_patterns=GitPatternsSnapshot(
			hotspots=['main.py'],
			stable_files=[],
			coupling_clusters=[],
		),
	)


@pytest.fixture
def fake_import_graph_result():
	return ImportGraphResult(
		centrality={'main.py': 0.5},
		cluster_id={'main.py': 0},
		clusters=[Cluster(id=0, files=('main.py',))],
	)


@pytest.mark.asyncio
async def test_orchestrator_happy_path(tmp_path, fake_git_result, fake_import_graph_result):
	with (
		patch('compass.collectors.orchestrator.GitLogCollector') as MockGit,
		patch('compass.collectors.orchestrator.AstGrepCollector') as MockAst,
		patch('compass.collectors.orchestrator.DocsReaderCollector') as MockDocs,
		patch('compass.collectors.orchestrator.ImportGraphCollector') as MockImport,
		patch('compass.collectors.orchestrator.AnalysisContextStore') as MockStore,
	):
		MockGit.return_value.collect = AsyncMock(return_value=fake_git_result)
		MockAst.return_value.collect = AsyncMock(
			return_value={'error_handling': ['except ValueError']}
		)
		MockDocs.return_value.collect = AsyncMock(return_value={'README.md': 'hello'})
		MockImport.return_value.collect = AsyncMock(return_value=fake_import_graph_result)
		MockStore.return_value.write = AsyncMock()

		orchestrator = CollectorOrchestrator()
		result = await orchestrator.run(tmp_path)

	assert isinstance(result, AnalysisContext)


@pytest.mark.asyncio
async def test_orchestrator_aborts_on_collector_failure(tmp_path, fake_import_graph_result):
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
		MockImport.return_value.collect = AsyncMock(return_value=fake_import_graph_result)

		orchestrator = CollectorOrchestrator()
		with pytest.raises(CollectorError):
			await orchestrator.run(tmp_path)
