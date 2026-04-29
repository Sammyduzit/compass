from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from compass.adapters.summary import SummaryAdapter, _validate_summary_response
from compass.config import CompassConfig
from compass.domain.analysis_context import AnalysisContext
from compass.domain.architecture_snapshot import ArchitectureSnapshot
from compass.domain.cluster import Cluster
from compass.domain.coupling_pair import CouplingPair
from compass.domain.file_score import FileScore
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot
from compass.errors import SchemaValidationError
from compass.paths import compass_paths


def _config() -> CompassConfig:
	return CompassConfig(target_path='/tmp/repo', adapters=['summary'], provider='claude')


def _analysis_context() -> AnalysisContext:
	return AnalysisContext(
		architecture=ArchitectureSnapshot(
			file_scores=[
				FileScore(
					path='src/main.py',
					churn=0.1,
					age=300,
					centrality=0.8,
					cluster_id=1,
					coupling_pairs=('src/base.py',),
				)
			],
			coupling_pairs=[CouplingPair(file_a='src/main.py', file_b='src/base.py', degree=3)],
			clusters=[Cluster(id=1, files=('src/main.py', 'src/base.py'))],
		),
		patterns={'error_handling': ['try/except sentinel pattern']},
		git_patterns=GitPatternsSnapshot(
			hotspots=['src/main.py'],
			stable_files=['src/base.py'],
			coupling_clusters=[['src/main.py', 'src/base.py']],
		),
		docs={'README.md': 'readme sentinel content'},
	)


_VALID_SUMMARY_RESPONSE = """\
# What this codebase does

A test repository for onboarding.

## Where to start reading

1. `src/main.py` — the entry point.

## JSON Output

```json
{
  "repo_name": "test-repo",
  "generated_at": "2026-01-01T00:00:00Z",
  "what_it_does": "A test repository for onboarding.",
  "read_first": [{"path": "src/main.py", "reason": "The entry point."}],
  "stable": [],
  "hotspots": [],
  "clusters": []
}
```
"""


@pytest.fixture
def adapter(tmp_path):
	config = _config()
	with patch('compass.adapters.base.get_provider') as mock_get:
		mock_provider = MagicMock()
		mock_provider.call = AsyncMock(return_value=_VALID_SUMMARY_RESPONSE)
		mock_get.return_value = mock_provider
		inst = SummaryAdapter(config, compass_paths(tmp_path))
		inst._provider = mock_provider
		return inst


# --- build_prompt ---


def test_build_prompt_includes_skeletons(adapter):
	context = _analysis_context()
	with patch(
		'compass.adapters.summary.render_skeletons',
		return_value={'src/main.py': 'def main(): pass'},
	):
		prompt = adapter.build_prompt(context, 'python')
	assert 'def main(): pass' in prompt


def test_build_prompt_includes_git_signals(adapter):
	context = _analysis_context()
	with patch('compass.adapters.summary.render_skeletons', return_value={}):
		prompt = adapter.build_prompt(context, 'python')
	assert 'hotspots' in prompt
	assert 'stable_files' in prompt
	assert 'coupling_clusters' in prompt


def test_build_prompt_excludes_ast_grep_patterns(adapter):
	context = _analysis_context()
	with patch('compass.adapters.summary.render_skeletons', return_value={}):
		prompt = adapter.build_prompt(context, 'python')
	assert 'error_handling' not in prompt
	assert 'try/except sentinel pattern' not in prompt


def test_build_prompt_excludes_docs(adapter):
	context = _analysis_context()
	with patch('compass.adapters.summary.render_skeletons', return_value={}):
		prompt = adapter.build_prompt(context, 'python')
	assert 'readme sentinel content' not in prompt


# --- _validate_summary_response ---


def test_validate_summary_response_returns_md_and_json():
	md, data = _validate_summary_response(_VALID_SUMMARY_RESPONSE)
	assert '# What this codebase does' in md
	assert data['repo_name'] == 'test-repo'


def test_validate_summary_response_raises_on_missing_json_block():
	with pytest.raises(ValueError, match='No JSON block'):
		_validate_summary_response('Just some markdown with no JSON block.')


def test_validate_summary_response_raises_on_invalid_schema():
	bad = (
		'# Summary\n\n'
		'## JSON Output\n\n'
		'```json\n'
		'{"repo_name": "x", "generated_at": "not-a-date",'
		' "what_it_does": "x", "read_first": [], "stable": [], "hotspots": [], "clusters": []}\n'
		'```'
	)
	with pytest.raises(ValueError, match='validation failed'):
		_validate_summary_response(bad)


def test_validate_summary_response_raises_on_empty_markdown():
	response = (
		'## JSON Output\n\n'
		'```json\n'
		'{"repo_name": "x", "generated_at": "2026-01-01T00:00:00Z",'
		' "what_it_does": "x", "read_first": [], "stable": [], "hotspots": [], "clusters": []}\n'
		'```'
	)
	with pytest.raises(ValueError, match='No markdown content'):
		_validate_summary_response(response)


# --- run ---


async def test_run_writes_summary_md(adapter, tmp_path):
	context = _analysis_context()
	with (
		patch('compass.adapters.summary.read_analysis_context', return_value=context),
		patch('compass.adapters.summary.render_skeletons', return_value={}),
		patch.object(
			adapter, 'call_provider', new_callable=AsyncMock, return_value=_VALID_SUMMARY_RESPONSE
		),
		patch('asyncio.sleep', new_callable=AsyncMock),
	):
		adapter._paths = compass_paths(tmp_path)
		await adapter.run()

	summary_md = tmp_path / '.compass' / 'output' / 'summary.md'
	assert summary_md.exists()
	assert '# What this codebase does' in summary_md.read_text()


async def test_run_writes_summary_json(adapter, tmp_path):
	context = _analysis_context()
	with (
		patch('compass.adapters.summary.read_analysis_context', return_value=context),
		patch('compass.adapters.summary.render_skeletons', return_value={}),
		patch.object(
			adapter, 'call_provider', new_callable=AsyncMock, return_value=_VALID_SUMMARY_RESPONSE
		),
		patch('asyncio.sleep', new_callable=AsyncMock),
	):
		adapter._paths = compass_paths(tmp_path)
		await adapter.run()

	summary_json = tmp_path / '.compass' / 'output' / 'summary.json'
	assert summary_json.exists()
	assert json.loads(summary_json.read_text())['repo_name'] == 'test-repo'


async def test_run_retries_once_on_invalid_response(adapter, tmp_path):
	context = _analysis_context()
	call_count = 0

	async def fake_provider(prompt: str) -> str:
		nonlocal call_count
		call_count += 1
		if call_count == 1:
			return 'no json block here'
		return _VALID_SUMMARY_RESPONSE

	with (
		patch('compass.adapters.summary.read_analysis_context', return_value=context),
		patch('compass.adapters.summary.render_skeletons', return_value={}),
		patch.object(adapter, 'call_provider', side_effect=fake_provider),
		patch('asyncio.sleep', new_callable=AsyncMock),
	):
		adapter._paths = compass_paths(tmp_path)
		await adapter.run()

	assert call_count == 2


async def test_run_raises_schema_error_after_second_failure(adapter, tmp_path):
	context = _analysis_context()
	with (
		patch('compass.adapters.summary.read_analysis_context', return_value=context),
		patch('compass.adapters.summary.render_skeletons', return_value={}),
		patch.object(
			adapter, 'call_provider', new_callable=AsyncMock, return_value='no json block here'
		),
		patch('asyncio.sleep', new_callable=AsyncMock),
	):
		adapter._paths = compass_paths(tmp_path)
		with pytest.raises(SchemaValidationError):
			await adapter.run()
