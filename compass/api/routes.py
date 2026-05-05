"""API routes for running Compass and reading generated outputs."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

from compass.api.models import (
	AdapterName,
	RulesOutputResponse,
	RunRequest,
	RunResponse,
	SummaryOutputResponse,
)
from compass.config import CompassConfig
from compass.paths import compass_paths
from compass.runner import run
from compass.schemas.rules_schema import RulesOutput
from compass.schemas.summary_schema import SummaryOutput

router = APIRouter()


@router.post('/run', response_model=RunResponse)
async def run_compass(request: RunRequest) -> RunResponse:
	config = CompassConfig(
		target_path=request.target_path,
		adapters=[adapter.value for adapter in request.adapters],
		provider=request.provider,
		lang=request.lang,
		reanalyze=request.reanalyze,
	)
	output_paths = await run(config)
	return RunResponse(output_paths=[str(path) for path in output_paths])


@router.get(
	'/output/{adapter}',
	response_model=SummaryOutputResponse | RulesOutputResponse,
)
async def read_output(
	adapter: AdapterName,
	target_path: str,
) -> SummaryOutputResponse | RulesOutputResponse:
	paths = compass_paths(target_path)

	if adapter is AdapterName.summary:
		path = paths.summary_json
		contents = _read_json_file(path)
		return SummaryOutputResponse(
			output_path=str(path),
			data=SummaryOutput.model_validate(contents),
		)

	path = paths.rules_yaml
	contents = _read_yaml_file(path)
	return RulesOutputResponse(
		output_path=str(path),
		data=RulesOutput.model_validate(contents),
	)


def _read_json_file(path: Path) -> dict[str, object]:
	if not path.is_file():
		raise HTTPException(status_code=404, detail=f'Output file not found: {path.name}')
	return json.loads(path.read_text(encoding='utf-8'))


def _read_yaml_file(path: Path) -> dict[str, object]:
	if not path.is_file():
		raise HTTPException(status_code=404, detail=f'Output file not found: {path.name}')
	return yaml.safe_load(path.read_text(encoding='utf-8'))
