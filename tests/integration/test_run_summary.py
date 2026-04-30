from __future__ import annotations

import asyncio
import json
import shutil
from collections.abc import Callable
from importlib.util import find_spec
from pathlib import Path

import pytest

from compass.config import CompassConfig
from compass.domain.cluster import Cluster
from compass.runner import run
from compass.schemas.summary_schema import validate_summary

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


class _SummaryProvider:
	cli_binary = 'integration-summary-provider'

	async def call(self, prompt: str) -> str:
		return _summary_response()


@pytest.mark.skipif(
	find_spec('compass.adapters.summary') is None,
	reason='SummaryAdapter is not available yet; finalize after issue #31 merges.',
)
@pytest.mark.parametrize(
	('fixture_name', 'language'),
	[
		('sample_repo_python', 'python'),
		('sample_repo_typescript', 'typescript'),
	],
)
def test_run_summary_pipeline_writes_schema_valid_summary_artifacts(
	integration_repo: Callable[[str], Path],
	monkeypatch: pytest.MonkeyPatch,
	fixture_name: str,
	language: str,
) -> None:
	_require_summary_integration_dependencies()
	_patch_integration_boundaries(monkeypatch)
	repo_path = integration_repo(fixture_name)

	asyncio.run(
		run(
			CompassConfig(
				target_path=str(repo_path),
				adapters=['summary'],
				provider='integration-summary',
				lang=language,
				reanalyze=True,
			)
		)
	)

	output_dir = repo_path / '.compass' / 'output'
	summary_md = output_dir / 'summary.md'
	summary_json = output_dir / 'summary.json'

	assert summary_md.is_file()
	assert summary_md.read_text(encoding='utf-8').strip()
	assert summary_json.is_file()

	data = json.loads(summary_json.read_text(encoding='utf-8'))
	result = validate_summary(data)
	assert result.valid, result.errors


def _require_summary_integration_dependencies() -> None:
	if shutil.which('ast-grep') is None and shutil.which('sg') is None:
		pytest.skip('ast-grep binary is required for integration tests.')
	pytest.importorskip('grep_ast')


def _patch_integration_boundaries(monkeypatch: pytest.MonkeyPatch) -> None:
	import compass.providers.base as provider_base

	monkeypatch.setitem(
		provider_base.PROVIDER_REGISTRY,
		'integration-summary',
		_SummaryProvider,
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


def _summary_response() -> str:
	return """
# Repository Summary

This fixture demonstrates service, API, and repository boundaries.

```json
{
  "repo_name": "sample-repo",
  "generated_at": "2026-04-30T00:00:00Z",
  "what_it_does": "This fixture demonstrates service, API, and repository boundaries.",
  "read_first": [
    {
      "path": "src/sample_app/service.py",
      "reason": "It shows the main orchestration boundary."
    }
  ],
  "stable": [
    {
      "path": "src/sample_app/models.py",
      "note": "It anchors the domain shape used by services."
    }
  ],
  "hotspots": [
    {
      "path": "src/sample_app/service.py",
      "note": "It changes when orchestration behavior changes."
    }
  ],
  "clusters": [
    {
      "id": 1,
      "summary": "Service files coordinate repository access and API entrypoints.",
      "files": ["src/sample_app/service.py", "src/sample_app/repository.py"],
      "coupling_pairs": [["src/sample_app/service.py", "src/sample_app/repository.py"]]
    }
  ]
}
```
""".strip()
