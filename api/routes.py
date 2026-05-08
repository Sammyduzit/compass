"""API routes for running Compass and reading generated outputs."""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.models import (
	AdapterName,
	JobOutputResponse,
	JobResponse,
	JobStatus,
	JobStatusResponse,
	RulesOutputResponse,
	RunRequest,
	SummaryOutputResponse,
)
from api.errors import _status_for_error
from compass.config import CompassConfig
from compass.errors import CompassError
from compass.paths import compass_paths
from compass.runner import run
from compass.schemas.rules_schema import RulesOutput
from compass.schemas.summary_schema import SummaryOutput

router = APIRouter()


@dataclass
class Job:
	status: JobStatus = JobStatus.queued
	output_paths: list[str] = field(default_factory=list)
	error: str | None = None
	exc: Exception | None = None


_jobs: dict[str, Job] = {}


async def _run_job(job_id: str, config: CompassConfig) -> None:
	job = _jobs[job_id]
	job.status = JobStatus.running
	try:
		output_paths = await run(config)
		job.output_paths = [str(p) for p in output_paths]
		job.status = JobStatus.done
	except Exception as exc:
		job.error = str(exc)
		job.exc = exc
		job.status = JobStatus.failed


@router.post('/run', response_model=JobResponse)
async def run_compass(request: RunRequest, background_tasks: BackgroundTasks) -> JobResponse:
	config = CompassConfig(
		target_path=str(request.target_path),
		adapters=[adapter.value for adapter in request.adapters],
		provider=request.provider,
		lang=request.lang,
		reanalyze=request.reanalyze,
	)
	job_id = str(uuid.uuid4())
	_jobs[job_id] = Job()
	background_tasks.add_task(_run_job, job_id, config)
	return JobResponse(job_id=job_id)


@router.get('/jobs/{job_id}', response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
	job = _jobs.get(job_id)
	if job is None:
		raise HTTPException(status_code=404, detail=f'Job not found: {job_id}')
	return JobStatusResponse(job_id=job_id, status=job.status, error=job.error)


@router.get('/jobs/{job_id}/output', response_model=JobOutputResponse)
async def get_job_output(job_id: str) -> JobOutputResponse:
	job = _jobs.get(job_id)
	if job is None:
		raise HTTPException(status_code=404, detail=f'Job not found: {job_id}')
	if job.status == JobStatus.failed:
		status_code = _status_for_error(job.exc) if isinstance(job.exc, CompassError) else 500
		raise HTTPException(status_code=status_code, detail=job.error)
	if job.status != JobStatus.done:
		raise HTTPException(status_code=409, detail=f'Job is not done yet: {job.status}')
	return JobOutputResponse(job_id=job_id, output_paths=job.output_paths)


@router.get(
	'/output/{adapter}',
	response_model=SummaryOutputResponse | RulesOutputResponse,
)
async def read_output(
	adapter: AdapterName,
	target_path: Path,
) -> SummaryOutputResponse | RulesOutputResponse:
	paths = compass_paths(target_path)

	if adapter == AdapterName.summary:
		path = paths.summary_json
		contents = await _read_json_file(path)
		return SummaryOutputResponse(
			output_path=str(path),
			data=SummaryOutput.model_validate(contents),
		)

	path = paths.rules_yaml
	contents = await _read_yaml_file(path)
	return RulesOutputResponse(
		output_path=str(path),
		data=RulesOutput.model_validate(contents),
	)


async def _read_json_file(path: Path) -> dict[str, object]:
	if not path.is_file():
		raise HTTPException(status_code=404, detail=f'Output file not found: {path.name}')
	return json.loads(await asyncio.to_thread(path.read_text, encoding='utf-8'))


async def _read_yaml_file(path: Path) -> dict[str, object]:
	if not path.is_file():
		raise HTTPException(status_code=404, detail=f'Output file not found: {path.name}')
	return yaml.safe_load(await asyncio.to_thread(path.read_text, encoding='utf-8'))
