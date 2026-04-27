<<<<<<< HEAD
from __future__ import annotations


from unittest.mock import AsyncMock, MagicMock, patch

from compass.adapters.orchestrator import Orchestrator
from compass.config import CompassConfig
from compass.errors import AdapterError


def _config(adapters: list[str], provider: str = 'claude') -> CompassConfig:
	return CompassConfig(target_path='/tmp/repo', adapters=adapters, provider=provider)


def _mock_adapter_cls(name: str, *, fail: bool = False) -> type:
	instance = MagicMock()
	if fail:
		instance.run = AsyncMock(side_effect=AdapterError(name, 'something went wrong'))
	else:
		instance.run = AsyncMock()
	cls = MagicMock(return_value=instance)
	return cls


async def test_orchestrator_runs_registered_adapter():
	mock_cls = _mock_adapter_cls('rules')
	registry = {'rules': mock_cls}
	config = _config(['rules'])

	with patch('compass.adapters.orchestrator.ADAPTER_REGISTRY', registry):
		orchestrator = Orchestrator(config)
		await orchestrator.run()

	mock_cls.return_value.run.assert_called_once()


async def test_orchestrator_skips_unknown_adapter():
	config = _config(['unknown_adapter'])
	registry: dict = {}

	with patch('compass.adapters.orchestrator.ADAPTER_REGISTRY', registry):
		orchestrator = Orchestrator(config)
		await orchestrator.run()
	# No exception raised — unknown adapter is skipped


async def test_orchestrator_continues_after_adapter_failure():
	failing_cls = _mock_adapter_cls('rules', fail=True)
	passing_cls = _mock_adapter_cls('summary')
	registry = {'rules': failing_cls, 'summary': passing_cls}
	config = _config(['rules', 'summary'])

	with patch('compass.adapters.orchestrator.ADAPTER_REGISTRY', registry):
		orchestrator = Orchestrator(config)
		await orchestrator.run()

	passing_cls.return_value.run.assert_called_once()


async def test_orchestrator_runs_only_requested_adapters():
	rules_cls = _mock_adapter_cls('rules')
	summary_cls = _mock_adapter_cls('summary')
	registry = {'rules': rules_cls, 'summary': summary_cls}
	config = _config(['rules'])

	with patch('compass.adapters.orchestrator.ADAPTER_REGISTRY', registry):
		orchestrator = Orchestrator(config)
		await orchestrator.run()

	rules_cls.return_value.run.assert_called_once()
	summary_cls.return_value.run.assert_not_called()
=======
from unittest.mock import AsyncMock, patch

import pytest

from compass.collectors.git_log import FileGitData, GitLogResult
from compass.collectors.import_graph import ImportGraphResult
from compass.collectors.orchestrator import CollectorOrchestrator
from compass.domain.analysis_context import AnalysisContext
from compass.domain.cluster import Cluster
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot
from compass.errors import CollectorError


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
>>>>>>> origin/dev
