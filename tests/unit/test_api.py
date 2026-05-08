from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from api.app import app
from api.models import JobStatus
from api.routes import Job, _jobs
from compass.config import CompassConfig
from compass.errors import PrerequisiteError, ProviderError, RepomixError


@pytest.fixture
def client() -> TestClient:
	return TestClient(app)


@pytest.fixture(autouse=True)
def clear_jobs() -> None:
	_jobs.clear()


def test_post_run_returns_job_id_and_runs_pipeline(
	client: TestClient,
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	calls: list[CompassConfig] = []
	output_path = tmp_path / '.compass' / 'output' / 'summary.json'

	async def fake_run(config: CompassConfig) -> list[Path]:
		calls.append(config)
		return [output_path]

	monkeypatch.setattr('api.routes.run', fake_run)

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
	job_id = response.json()['job_id']
	assert job_id
	# BackgroundTasks runs synchronously in TestClient — job is done by the time we assert
	assert _jobs[job_id].status == JobStatus.done
	assert _jobs[job_id].output_paths == [str(output_path)]
	assert calls == [
		CompassConfig(
			target_path=str(tmp_path),
			adapters=['summary'],
			provider='claude',
			lang='python',
			reanalyze=True,
		)
	]


@pytest.mark.parametrize(
	('exc', 'expected_status'),
	[
		(PrerequisiteError('repomix', 'missing binary.', 'brew install repomix'), 422),
		(ProviderError('summary', 'claude', 'timeout'), 502),
		(RepomixError('repomix failed.'), 503),
	],
)
def test_job_output_maps_compass_errors_to_http_status(
	client: TestClient,
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
	exc: Exception,
	expected_status: int,
) -> None:
	async def fake_run(_config: CompassConfig) -> list[Path]:
		raise exc

	monkeypatch.setattr('api.routes.run', fake_run)

	response = client.post(
		'/run',
		json={'target_path': str(tmp_path), 'adapters': ['summary']},
	)

	assert response.status_code == 200
	job_id = response.json()['job_id']
	assert _jobs[job_id].status == JobStatus.failed

	output_response = client.get(f'/jobs/{job_id}/output')
	assert output_response.status_code == expected_status


def test_get_job_status_returns_current_status(client: TestClient) -> None:
	_jobs['test-job'] = Job(status=JobStatus.running)

	response = client.get('/jobs/test-job')

	assert response.status_code == 200
	assert response.json() == {'job_id': 'test-job', 'status': 'running', 'error': None}


def test_get_job_status_returns_404_for_unknown_job(client: TestClient) -> None:
	response = client.get('/jobs/nonexistent')

	assert response.status_code == 404


def test_get_job_output_returns_paths_when_done(client: TestClient, tmp_path: Path) -> None:
	path = str(tmp_path / '.compass' / 'output' / 'summary.json')
	_jobs['test-job'] = Job(status=JobStatus.done, output_paths=[path])

	response = client.get('/jobs/test-job/output')

	assert response.status_code == 200
	assert response.json() == {'job_id': 'test-job', 'output_paths': [path]}


def test_get_job_output_returns_409_when_not_done(client: TestClient) -> None:
	_jobs['test-job'] = Job(status=JobStatus.running)

	response = client.get('/jobs/test-job/output')

	assert response.status_code == 409


def test_get_job_output_returns_500_for_unexpected_errors(client: TestClient) -> None:
	_jobs['test-job'] = Job(
		status=JobStatus.failed, error='something went wrong', exc=RuntimeError('oops')
	)

	response = client.get('/jobs/test-job/output')

	assert response.status_code == 500
	assert response.json()['detail'] == 'something went wrong'


def test_get_job_output_returns_404_for_unknown_job(client: TestClient) -> None:
	response = client.get('/jobs/nonexistent/output')

	assert response.status_code == 404


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
