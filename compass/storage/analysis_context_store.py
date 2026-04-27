"""Read and write persisted AnalysisContext JSON."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from dacite import Config, from_dict

from compass.domain.analysis_context import AnalysisContext
from compass.paths import compass_paths


def read_analysis_context(target_path: str | Path) -> AnalysisContext:
	"""Read ``.compass/analysis_context.json``."""

	path = compass_paths(target_path).analysis_context
	with path.open(encoding='utf-8') as file:
		data = json.load(file)
	if not isinstance(data, dict):
		raise ValueError('analysis_context.json must contain a JSON object')
	return from_dict(AnalysisContext, data, Config(cast=[tuple]))


def write_analysis_context(target_path: str | Path, analysis_context: Any) -> Path:
	"""Serialize an AnalysisContext-like object to ``analysis_context.json``."""

	path = compass_paths(target_path).analysis_context
	path.parent.mkdir(parents=True, exist_ok=True)
	payload = _to_jsonable(analysis_context)
	with path.open('w', encoding='utf-8') as file:
		json.dump(payload, file, indent=2, sort_keys=True)
		file.write('\n')
	return path


def _to_jsonable(value: Any) -> Any:
	if is_dataclass(value) and not isinstance(value, type):
		return asdict(value)
	if isinstance(value, dict):
		return {str(key): _to_jsonable(item) for key, item in value.items()}
	if isinstance(value, (list, tuple)):
		return [_to_jsonable(item) for item in value]
	if hasattr(value, 'to_dict') and callable(value.to_dict):
		return value.to_dict()
	return value
