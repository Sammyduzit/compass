"""Pipeline orchestration for Compass."""

from __future__ import annotations

import asyncio
from importlib import import_module
from pathlib import Path
from typing import Any

from compass.config import CompassConfig
from compass.paths import compass_paths
from compass.storage import (
	is_stale,
	read_analysis_context,
	write_analysis_context,
	write_current_repo_state,
)


async def run(config: CompassConfig) -> list[Any]:
	"""Run the Compass pipeline for a target repository."""

	target_path = Path(config.target_path)

	await _check_prerequisites()
	language = _detect_language(config, target_path)

	if _should_run_phase_one(config, target_path):
		analysis_context = await _collect_analysis_context(config, language)
		write_analysis_context(target_path, analysis_context)
		write_current_repo_state(target_path)
	else:
		analysis_context = read_analysis_context(target_path)

	return await _run_adapters(config, analysis_context, language)


def _should_run_phase_one(config: CompassConfig, target_path: Path) -> bool:
	if config.reanalyze:
		return True
	if not compass_paths(target_path).analysis_context.exists():
		return True
	return is_stale(target_path)


async def _check_prerequisites() -> None:
	module = import_module('compass.prerequisites')
	check = getattr(module, 'check')
	result = check()
	if asyncio.iscoroutine(result):
		await result


def _detect_language(config: CompassConfig, target_path: Path) -> str:
	module = import_module('compass.language_detection')
	detect = getattr(module, 'detect')
	return detect(target_path, override=config.lang)


async def _collect_analysis_context(config: CompassConfig, language: str) -> Any:
	orchestrator_class = _load_collector_orchestrator()
	orchestrator = _build_orchestrator(orchestrator_class, config, language)
	return await _call_async_method(orchestrator, 'collect', config.target_path)


async def _run_adapters(config: CompassConfig, analysis_context: Any, language: str) -> list[Any]:
	orchestrator_class = _load_adapter_orchestrator()
	orchestrator = _build_orchestrator(orchestrator_class, config, language)
	results = await _call_async_method(orchestrator, 'run', analysis_context)
	if results is None:
		return []
	if isinstance(results, list):
		return results
	return [results]


def _load_collector_orchestrator() -> type[Any]:
	module = import_module('compass.collectors.orchestrator')
	return getattr(module, 'CollectorOrchestrator')


def _load_adapter_orchestrator() -> type[Any]:
	module = import_module('compass.adapters.orchestrator')
	return getattr(module, 'AdapterOrchestrator')


def _build_orchestrator(
	orchestrator_class: type[Any],
	config: CompassConfig,
	language: str,
) -> Any:
	return orchestrator_class(config=config, language=language)


async def _call_async_method(instance: Any, method_name: str, *args: Any) -> Any:
	method = getattr(instance, method_name)
	result = method(*args)
	if asyncio.iscoroutine(result):
		return await result
	return result
