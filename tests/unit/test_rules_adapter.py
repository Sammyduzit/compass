from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml

from compass.adapters.rules import RulesAdapter
from compass.config import CompassConfig
from compass.domain.analysis_context import AnalysisContext
from compass.domain.architecture_snapshot import ArchitectureSnapshot
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot

from compass.domain.file_score import FileScore
from compass.errors import SchemaValidationError
from compass.paths import compass_paths
from compass.schemas.rules_schema import RulesOutput


def _config() -> CompassConfig:
	return CompassConfig(target_path='/tmp/repo', adapters=['rules'], provider='claude')


def _make_context(tmp_path) -> AnalysisContext:
	fake_file = tmp_path / 'path.py'
	fake_file.write_text('def foo(): pass')
	return AnalysisContext(
		architecture=ArchitectureSnapshot(
			file_scores=[
				FileScore(
					path=str(fake_file),
					churn=0.89,
					age=62,
					centrality=0.3,
					cluster_id=5,
					coupling_pairs=('this/is/path/2.py', 'this/is/path/1.py'),
				)
			],
			coupling_pairs=[],
			clusters=[],
		),
		patterns={
			'error_handling': ['except ValueError as e: raise ValidationError(str(e)) from e']
		},
		git_patterns=GitPatternsSnapshot(
			hotspots=['src/main.py'], stable_files=['src/config.py'], coupling_clusters=[]
		),
		docs={'codestyle': 'this is code'},
	)


def _make_context_with_files(*files: Path) -> AnalysisContext:
	return AnalysisContext(
		architecture=ArchitectureSnapshot(
			file_scores=[
				FileScore(
					path=str(file),
					churn=0.89 - (index * 0.1),
					age=62,
					centrality=1.0 - (index * 0.1),
					cluster_id=5,
					coupling_pairs=('this/is/path/2.py', 'this/is/path/1.py'),
				)
				for index, file in enumerate(files)
			],
			coupling_pairs=[],
			clusters=[],
		),
		patterns={
			'error_handling': ['except ValueError as e: raise ValidationError(str(e)) from e']
		},
		git_patterns=GitPatternsSnapshot(
			hotspots=['src/main.py'], stable_files=['src/config.py'], coupling_clusters=[]
		),
		docs={'codestyle': 'this is code'},
	)


def _valid_yaml() -> str:
	return """clusters:
  - name: Error Handling
    context: How errors are handled
    golden_file: src/main.py
    rules:
      - id: err-01
        rule: Always catch specific exceptions
        why: Broad catches hide bugs
        example: except ValueError
"""


def _prompt_input(prompt: str) -> dict:
	input_block = prompt.split('## Input\n\n```json\n')[-1]
	return json.loads(input_block.rsplit('\n```', 1)[0])


@pytest.fixture
def adapter(tmp_path):
	config = _config()
	with patch('compass.adapters.base.get_provider') as mock_get:
		mock_provider = MagicMock()
		mock_provider.call = AsyncMock(return_value='provider response')
		mock_get.return_value = mock_provider
		inst = RulesAdapter(config, compass_paths(tmp_path))
		inst._provider = mock_provider
		return inst


# --- parse_reconciliation_output ---


def test_parse_reconciliation_output_success(adapter):
	raw = (
		'Some text.\n\n'
		'### FINAL YAML OUTPUT ###\n'
		'```yaml\n'
		'clusters:\n'
		'  - name: Error Handling\n'
		'    context: How errors are handled across the codebase\n'
		'    golden_file: src/main.py\n'
		'    rules:\n'
		'      - id: err-01\n'
		'        rule: Always catch specific exceptions\n'
		'        why: Broad catches hide bugs\n'
		'        example: "except ValueError as e"\n'
		'```\n'
	)

	result = adapter.parse_reconciliation_output(raw)

	assert 'clusters:' in result
	assert 'err-01' in result


def test_parse_reconciliation_output_raises_on_missing_header(adapter):
	raw = 'Here is the yaml:\n```yaml\nclusters:\n  typing: []\n```\n'

	with pytest.raises(ValueError, match='missing strict section header'):
		adapter.parse_reconciliation_output(raw)


def test_build_prompt(adapter, tmp_path):
	fake_analysis_context = _make_context(tmp_path)
	prompt = adapter.build_prompt(
		fake_analysis_context,
		skeletons='def foo(): pass',
		repomix_bodies='class Bar: ...',
		domain='myrepo',
		lang='python',
	)

	assert 'def foo(): pass' in prompt
	assert 'class Bar: ...' in prompt
	assert 'error_handling' in prompt
	assert 'except ValueError' in prompt
	assert 'src/config.py' in prompt
	assert 'codestyle' in prompt
	assert 'this is code' in prompt
	assert str(tmp_path / 'path.py') in prompt


def test_build_prompt_skips_binary_golden_file(adapter, tmp_path):
	text_file = tmp_path / 'text.py'
	binary_file = tmp_path / 'binary.py'
	text_file.write_text('def foo():\n    return 1\n')
	binary_file.write_bytes(b'\xff\xfe\x00\x00')
	context = _make_context_with_files(binary_file, text_file)

	prompt = adapter.build_prompt(
		context,
		skeletons='def foo(): pass',
		repomix_bodies='class Bar: ...',
		domain='myrepo',
		lang='python',
	)
	input_dict = _prompt_input(prompt)

	assert input_dict['golden_files'] == [
		{'path': str(text_file), 'content': 'def foo():\n    return 1\n'}
	]


def test_build_reconciliation_prompt_skips_binary_golden_file(adapter, tmp_path):
	text_file = tmp_path / 'text.py'
	binary_file = tmp_path / 'binary.py'
	text_file.write_text('def foo():\n    return 1\n')
	binary_file.write_bytes(b'\xff\xfe\x00\x00')
	context = _make_context_with_files(binary_file, text_file)

	prompt = adapter.build_reconciliation_prompt(
		context, extracted_rules='rules', domain='myrepo', lang='python'
	)
	input_dict = _prompt_input(prompt)

	assert input_dict['golden_files'] == [
		{'path': str(text_file), 'content': 'def foo():\n    return 1\n'}
	]


async def test_validate_output_passes_valid_schema(adapter):
	adapter.call_provider = AsyncMock(return_value=_valid_yaml())

	def validator(raw: str):
		return RulesOutput.model_validate(yaml.safe_load(raw))

	result = await adapter.validate_output(_valid_yaml(), validator, 'prompt')

	assert result is not None


async def test_validate_output_retires_once_on_invalid(adapter):
	adapter.call_provider = AsyncMock(side_effect=[_valid_yaml()])

	def validator(raw: str):
		return RulesOutput.model_validate(yaml.safe_load(raw))

	with patch('asyncio.sleep', new_callable=AsyncMock):
		result = await adapter.validate_output('invalid yaml', validator, 'prompt')

	assert result is not None
	adapter.call_provider.assert_called_once()


async def test_validate_output_hard_error_after_second_failure(adapter):
	adapter.call_provider = AsyncMock(side_effect=['invalid yaml'])

	def validator(raw: str):
		return RulesOutput.model_validate(yaml.safe_load(raw))

	with patch('asyncio.sleep', new_callable=AsyncMock):
		with pytest.raises(SchemaValidationError):
			await adapter.validate_output('invalid yaml', validator, 'prompt')
