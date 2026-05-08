"""Integration tests for the async job-queue API flow."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import api.routes as routes_module
from api.app import app
from compass.domain.cluster import Cluster
from compass.errors import PrerequisiteError

pytestmark = pytest.mark.integration


class _FakeImportGraphCollector:
	async def collect(self, target_path: Path) -> object:
		files = _source_files(target_path)
		cluster_files = tuple(files[: min(3, len(files))])
		return type(
			'ImportGraphResult',
			(),
			{
				'centrality': {p: 1.0 if p in cluster_files else 0.2 for p in files},
				'cluster_id': {p: 1 if p in cluster_files else 2 for p in files},
				'clusters': [Cluster(id=1, files=cluster_files)],
			},
		)()


class _FakeSummaryProvider:
	cli_binary = 'integration-job-queue-provider'

	async def call(self, prompt: str) -> str:
		return _summary_response()



@pytest.fixture()
def client() -> TestClient:
	return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_job_store() -> Iterator[None]:
	routes_module._jobs.clear()
	yield
	routes_module._jobs.clear()


def _patch_boundaries(
	monkeypatch: pytest.MonkeyPatch,
	provider_class: type = _FakeSummaryProvider,
) -> None:
	import compass.providers.base as provider_base

	monkeypatch.setitem(provider_base.PROVIDER_REGISTRY, 'integration-job-queue', provider_class)
	monkeypatch.setattr('compass.prerequisites.check', lambda: None)
	monkeypatch.setattr(
		'compass.collectors.orchestrator.ImportGraphCollector',
		_FakeImportGraphCollector,
	)


def _poll_until_done(client: TestClient, job_id: str, max_attempts: int = 20) -> dict:
	for _ in range(max_attempts):
		r = client.get(f'/jobs/{job_id}')
		assert r.status_code == 200
		if r.json()['status'] in ('done', 'failed'):
			return r.json()
	pytest.fail(f'Job {job_id} did not reach terminal state after {max_attempts} attempts')


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

## JSON Output

```json
{
  "repo_name": "sample-repo",
  "generated_at": "2026-04-30T00:00:00Z",
  "what_it_does": "Fixture repo for job queue integration tests.",
  "read_first": [{"path": "src/sample_app/service.py", "reason": "Entry point."}],
  "stable": [{"path": "src/sample_app/models.py", "note": "Stable core."}],
  "hotspots": [{"path": "src/sample_app/service.py", "note": "Hot path."}],
  "clusters": [{
    "id": 1,
    "summary": "Service layer.",
    "files": ["src/sample_app/service.py"],
    "coupling_pairs": [["src/sample_app/service.py", "src/sample_app/repository.py"]]
  }]
}
```
""".strip()


def test_full_round_trip(
	client: TestClient,
	monkeypatch: pytest.MonkeyPatch,
	integration_repo: Callable[[str], Path],
) -> None:
	_patch_boundaries(monkeypatch)
	repo_path = integration_repo('sample_repo_python')

	post_response = client.post(
		'/run',
		json={
			'target_path': str(repo_path),
			'adapters': ['summary'],
			'provider': 'integration-job-queue',
			'lang': 'python',
			'reanalyze': True,
		},
	)
	assert post_response.status_code == 200
	job_id = post_response.json()['job_id']
	assert job_id

	final_status = _poll_until_done(client, job_id)
	assert final_status['status'] == 'done'

	output_response = client.get(f'/jobs/{job_id}/output')
	assert output_response.status_code == 200
	data = output_response.json()
	assert data['job_id'] == job_id
	assert len(data['output_paths']) > 0
	assert any('summary' in p for p in data['output_paths'])


def test_job_transitions_queued_running_done(
	client: TestClient,
	monkeypatch: pytest.MonkeyPatch,
	integration_repo: Callable[[str], Path],
) -> None:
	seen_states: list[str] = []
	original_run_job = routes_module._run_job

	async def _recording_run_job(job_id: str, config: object) -> None:
		seen_states.append(routes_module._jobs[job_id].status.value)
		await original_run_job(job_id, config)
		seen_states.append(routes_module._jobs[job_id].status.value)

	_patch_boundaries(monkeypatch)
	monkeypatch.setattr(routes_module, '_run_job', _recording_run_job)
	repo_path = integration_repo('sample_repo_python')

	response = client.post(
		'/run',
		json={
			'target_path': str(repo_path),
			'adapters': ['summary'],
			'provider': 'integration-job-queue',
			'lang': 'python',
			'reanalyze': True,
		},
	)
	assert response.status_code == 200
	_poll_until_done(client, response.json()['job_id'])

	assert 'queued' in seen_states
	assert 'done' in seen_states


def test_failed_job_returns_correct_http_status_on_output_endpoint(
	client: TestClient,
	monkeypatch: pytest.MonkeyPatch,
	integration_repo: Callable[[str], Path],
) -> None:
	def _raise_prereq() -> None:
		raise PrerequisiteError('repomix', 'missing binary', 'brew install repomix')

	_patch_boundaries(monkeypatch)
	monkeypatch.setattr('compass.prerequisites.check', _raise_prereq)
	repo_path = integration_repo('sample_repo_python')

	post_response = client.post(
		'/run',
		json={
			'target_path': str(repo_path),
			'adapters': ['summary'],
			'provider': 'integration-job-queue',
			'lang': 'python',
			'reanalyze': True,
		},
	)
	assert post_response.status_code == 200
	job_id = post_response.json()['job_id']

	final_status = _poll_until_done(client, job_id)
	assert final_status['status'] == 'failed'
	assert final_status['error']

	output_response = client.get(f'/jobs/{job_id}/output')
	assert output_response.status_code == 422


def test_concurrent_jobs_do_not_interfere(
	client: TestClient,
	monkeypatch: pytest.MonkeyPatch,
	integration_repo: Callable[[str], Path],
) -> None:
	_patch_boundaries(monkeypatch)
	repo_a = integration_repo('sample_repo_python')
	repo_b = integration_repo('sample_repo_typescript')

	response_a = client.post(
		'/run',
		json={
			'target_path': str(repo_a),
			'adapters': ['summary'],
			'provider': 'integration-job-queue',
			'lang': 'python',
			'reanalyze': True,
		},
	)
	response_b = client.post(
		'/run',
		json={
			'target_path': str(repo_b),
			'adapters': ['summary'],
			'provider': 'integration-job-queue',
			'lang': 'typescript',
			'reanalyze': True,
		},
	)

	assert response_a.status_code == 200
	assert response_b.status_code == 200
	job_id_a = response_a.json()['job_id']
	job_id_b = response_b.json()['job_id']
	assert job_id_a != job_id_b

	_poll_until_done(client, job_id_a)
	_poll_until_done(client, job_id_b)

	output_a = client.get(f'/jobs/{job_id_a}/output').json()
	output_b = client.get(f'/jobs/{job_id_b}/output').json()

	assert output_a['output_paths'] != output_b['output_paths']
	assert all(str(repo_a) in p for p in output_a['output_paths'])
	assert all(str(repo_b) in p for p in output_b['output_paths'])
