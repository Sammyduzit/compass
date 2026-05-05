from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from compass.api.app import app
from compass.config import CompassConfig
from compass.errors import PrerequisiteError, ProviderError, RepomixError


@pytest.fixture
def client() -> TestClient:
	return TestClient(app)


def test_post_run_calls_runner_and_returns_output_paths(
	client: TestClient,
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	calls: list[CompassConfig] = []

	async def fake_run(config: CompassConfig) -> list[Path]:
		calls.append(config)
		return [tmp_path / '.compass' / 'output' / 'summary.json']

	monkeypatch.setattr('compass.api.routes.run', fake_run)

	response = client.post(
		'/run',
		json={
			'target_path': str(tmp_path),
			'adapters': ['summary'],
			'provider': 'claude',
			'lang': 'python',
			'reanalyze': True,
		},
	)

	assert response.status_code == 200
	assert response.json() == {
		'output_paths': [str(tmp_path / '.compass' / 'output' / 'summary.json')]
	}
	assert calls == [
		CompassConfig(
			target_path=str(tmp_path),
			adapters=['summary'],
			provider='claude',
			lang='python',
			reanalyze=True,
		)
	]


def test_get_output_summary_returns_schema_aligned_json(
	client: TestClient,
	tmp_path: Path,
) -> None:
	output_dir = tmp_path / '.compass' / 'output'
	output_dir.mkdir(parents=True)
	summary_path = output_dir / 'summary.json'
	summary_path.write_text(
		json.dumps(
			{
				'repo_name': 'sample-repo',
				'generated_at': '2026-05-05T00:00:00Z',
				'what_it_does': 'Summarizes the repository.',
				'read_first': [{'path': 'src/app.py', 'reason': 'Entry point.'}],
				'stable': [{'path': 'src/models.py', 'note': 'Stable core.'}],
				'hotspots': [{'path': 'src/app.py', 'note': 'Frequently changed.'}],
				'clusters': [
					{
						'id': 1,
						'summary': 'Main cluster.',
						'files': ['src/app.py'],
						'coupling_pairs': [['src/app.py', 'src/models.py']],
					}
				],
			}
		),
		encoding='utf-8',
	)

	response = client.get('/output/summary', params={'target_path': str(tmp_path)})

	assert response.status_code == 200
	assert response.json()['adapter'] == 'summary'
	assert response.json()['output_path'] == str(summary_path)
	assert response.json()['data']['repo_name'] == 'sample-repo'


def test_get_output_rules_returns_schema_aligned_json(
	client: TestClient,
	tmp_path: Path,
) -> None:
	output_dir = tmp_path / '.compass' / 'output'
	output_dir.mkdir(parents=True)
	rules_path = output_dir / 'rules.yaml'
	rules_path.write_text(
		yaml.safe_dump(
			{
				'clusters': [
					{
						'name': 'Service Boundaries',
						'context': 'Keep layers separated.',
						'golden_file': 'src/service.py',
						'rules': [
							{
								'id': 'service-boundary-01',
								'rule': 'Keep service boundaries explicit.',
								'why': 'Clear seams reduce regressions.',
								'example': 'UserService().load()',
							}
						],
					}
				]
			}
		),
		encoding='utf-8',
	)

	response = client.get('/output/rules', params={'target_path': str(tmp_path)})

	assert response.status_code == 200
	assert response.json()['adapter'] == 'rules'
	assert response.json()['output_path'] == str(rules_path)
	assert response.json()['data']['clusters'][0]['name'] == 'Service Boundaries'


def test_get_output_returns_404_when_artifact_is_missing(
	client: TestClient,
	tmp_path: Path,
) -> None:
	response = client.get('/output/summary', params={'target_path': str(tmp_path)})

	assert response.status_code == 404
	assert response.json() == {'detail': 'Output file not found: summary.json'}


def test_compass_errors_are_mapped_to_http_status_codes(
	client: TestClient,
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	async def fake_run_prereq(config: CompassConfig) -> list[Path]:
		raise PrerequisiteError('repomix', 'missing binary.', 'brew install repomix')

	monkeypatch.setattr('compass.api.routes.run', fake_run_prereq)

	response = client.post(
		'/run',
		json={'target_path': str(tmp_path), 'adapters': ['rules']},
	)

	assert response.status_code == 422

	async def fake_run_provider(config: CompassConfig) -> list[Path]:
		raise ProviderError('summary', 'claude', 'timeout')

	monkeypatch.setattr('compass.api.routes.run', fake_run_provider)

	response = client.post(
		'/run',
		json={'target_path': str(tmp_path), 'adapters': ['summary']},
	)

	assert response.status_code == 502


def test_post_run_rejects_empty_adapters_list(
	client: TestClient,
	tmp_path: Path,
) -> None:
	response = client.post(
		'/run',
		json={'target_path': str(tmp_path), 'adapters': []},
	)

	assert response.status_code == 422


def test_post_run_rejects_invalid_adapter_name(
	client: TestClient,
	tmp_path: Path,
) -> None:
	response = client.post(
		'/run',
		json={'target_path': str(tmp_path), 'adapters': ['nonexistent']},
	)

	assert response.status_code == 422


def test_post_run_rejects_missing_body(client: TestClient) -> None:
	response = client.post('/run')

	assert response.status_code == 422


def test_repomix_error_is_mapped_to_503(
	client: TestClient,
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	async def fake_run(_config: CompassConfig) -> list[Path]:
		raise RepomixError('repomix failed.')

	monkeypatch.setattr('compass.api.routes.run', fake_run)

	response = client.post(
		'/run',
		json={'target_path': str(tmp_path), 'adapters': ['summary']},
	)

	assert response.status_code == 503
