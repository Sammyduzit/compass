from __future__ import annotations

import asyncio
import shutil
from collections.abc import Callable
from importlib.util import find_spec
from pathlib import Path

import pytest
import yaml

from compass.config import CompassConfig
from compass.domain.cluster import Cluster
from compass.runner import run
from compass.schemas.rules_schema import validate_rules

pytestmark = pytest.mark.integration


class _FakeImportGraphCollector:
	async def collect(self, target_path: Path) -> object:
		files = _source_files(target_path)
		cluster_files = tuple(files[: min(3, len(files))])
		return type(
			'ImportGraphResult',
			(),
			{
				'centrality': {path: 1.0 if path in cluster_files else 0.2 for path in files},
				'cluster_id': {path: 1 if path in cluster_files else 2 for path in files},
				'clusters': [Cluster(id=1, files=cluster_files)],
			},
		)()


class _RulesProvider:
	cli_binary = 'integration-rules-provider'

	async def call(self, prompt: str) -> str:
		return _rules_yaml()


@pytest.mark.skipif(
	find_spec('compass.adapters.rules') is None,
	reason='RulesAdapter is not available yet; finalize after issue #30 merges.',
)
@pytest.mark.parametrize(
	('fixture_name', 'language'),
	[
		('sample_repo_python', 'python'),
		('sample_repo_typescript', 'typescript'),
	],
)
def test_run_rules_pipeline_writes_schema_valid_rules_yaml(
	integration_repo: Callable[[str], Path],
	monkeypatch: pytest.MonkeyPatch,
	fixture_name: str,
	language: str,
) -> None:
	_require_rules_integration_dependencies()
	_patch_integration_boundaries(monkeypatch)
	repo_path = integration_repo(fixture_name)

	asyncio.run(
		run(
			CompassConfig(
				target_path=str(repo_path),
				adapters=['rules'],
				provider='integration-rules',
				lang=language,
				reanalyze=True,
			)
		)
	)

	rules_path = repo_path / '.compass' / 'output' / 'rules.yaml'
	assert rules_path.is_file()

	data = yaml.safe_load(rules_path.read_text(encoding='utf-8'))
	result = validate_rules(data)
	assert result.valid, result.errors
	assert data['clusters']


def _require_rules_integration_dependencies() -> None:
	if shutil.which('ast-grep') is None and shutil.which('sg') is None:
		pytest.skip('ast-grep binary is required for integration tests.')
	if shutil.which('repomix') is None:
		pytest.skip('repomix binary is required for rules integration tests.')
	pytest.importorskip('grep_ast')


def _patch_integration_boundaries(monkeypatch: pytest.MonkeyPatch) -> None:
	import compass.providers.base as provider_base

	monkeypatch.setitem(
		provider_base.PROVIDER_REGISTRY,
		'integration-rules',
		_RulesProvider,
	)
	monkeypatch.setattr('compass.prerequisites.check', lambda: None)
	monkeypatch.setattr(
		'compass.collectors.orchestrator.ImportGraphCollector',
		_FakeImportGraphCollector,
	)


def _source_files(target_path: Path) -> list[str]:
	return sorted(
		str(path.relative_to(target_path))
		for path in target_path.rglob('*')
		if path.is_file()
		and '.git' not in path.parts
		and '.compass' not in path.parts
		and path.suffix in {'.py', '.ts'}
	)


def _rules_yaml() -> str:
	return """
clusters:
  - name: Service Boundaries
    context: Keep service orchestration separated from persistence and API entrypoints.
    golden_file: src/sample_app/service.py
    rules:
      - id: service-boundary-01
        rule: Services must coordinate repositories instead of exposing storage details.
        why: Keeping storage access behind service methods makes downstream callers stable.
        example: |
          class UserService:
              def load(self, name):
                  return self.repository.get(name)
""".strip()
