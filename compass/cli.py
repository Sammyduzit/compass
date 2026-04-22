"""Thin CLI entry point for Compass."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

try:
	import yaml
except ImportError:  # pragma: no cover - exercised only in minimal local environments.
	yaml = None

from compass.config import CompassConfig
from compass.errors import CompassError, ConfigError
from compass.log import configure_logging


ALL_ADAPTERS = ['rules', 'summary']
ALLOWED_PROVIDERS = {'claude', 'codex'}
ALLOWED_LANGUAGES = {'auto', 'python', 'typescript'}
CONFIG_FILENAME = 'config.yaml'


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog='compass',
		description='Analyze a repository and generate Compass outputs.',
	)
	parser.add_argument('target_path', help='Path to the target repository.')
	parser.add_argument(
		'--adapters',
		default=None,
		help='Comma-separated adapters to run, or "all". Defaults to "rules".',
	)
	parser.add_argument(
		'--provider',
		choices=tuple(sorted(ALLOWED_PROVIDERS)),
		help='LLM provider to use. Falls back to config.yaml when omitted.',
	)
	parser.add_argument(
		'--lang',
		default=None,
		choices=tuple(sorted(ALLOWED_LANGUAGES)),
		help='Target language. Defaults to "auto".',
	)
	parser.add_argument(
		'--reanalyze',
		action='store_true',
		help='Rebuild analysis context instead of reusing cached state.',
	)
	return parser


def parse_adapters(value: str | None) -> list[str]:
	if value is None:
		return ['rules']

	adapters = [adapter.strip() for adapter in value.split(',') if adapter.strip()]
	if not adapters:
		raise ConfigError('adapters', value, 'comma-separated adapters or "all"')
	if adapters == ['all']:
		return ALL_ADAPTERS.copy()

	seen: set[str] = set()
	normalized: list[str] = []
	for adapter in adapters:
		if adapter not in ALL_ADAPTERS:
			raise ConfigError('adapters', adapter, f'one of {", ".join(ALL_ADAPTERS)} or "all"')
		if adapter not in seen:
			seen.add(adapter)
			normalized.append(adapter)
	return normalized


def load_merged_config(target_path: str | Path) -> dict[str, Any]:
	target_repo = Path(target_path)
	merged: dict[str, Any] = {}
	for config_path in _config_paths(target_repo):
		merged.update(_load_config_file(config_path))
	return merged


def build_config(args: argparse.Namespace) -> CompassConfig:
	file_config = load_merged_config(args.target_path)

	provider = args.provider or _normalize_provider(file_config.get('default_provider'))
	lang = args.lang or _normalize_lang(file_config.get('lang'))

	return CompassConfig(
		target_path=args.target_path,
		adapters=parse_adapters(args.adapters),
		provider=provider,
		lang=lang,
		reanalyze=args.reanalyze,
	)


def main(argv: list[str] | None = None) -> int:
	parser = build_parser()
	args = parser.parse_args(argv)
	configure_logging()

	try:
		config = build_config(args)
		_run_runner(config)
	except CompassError as error:
		print(str(error), file=sys.stderr)
		return 1

	return 0


def _run_runner(config: CompassConfig) -> None:
	from compass import runner

	asyncio.run(runner.run(config))


def _config_paths(target_repo: Path) -> tuple[Path, Path]:
	return (
		Path.home() / '.compass' / CONFIG_FILENAME,
		target_repo / '.compass' / CONFIG_FILENAME,
	)


def _load_config_file(path: Path) -> dict[str, Any]:
	if not path.exists():
		return {}

	data = _parse_config_text(path.read_text(encoding='utf-8'))

	if data is None:
		return {}
	if not isinstance(data, dict):
		raise ConfigError(str(path), data, 'a YAML mapping')

	_validate_config_keys(path, data)
	return data


def _parse_config_text(content: str) -> dict[str, Any] | None:
	if yaml is not None:
		return yaml.safe_load(content)

	data: dict[str, str] = {}
	for raw_line in content.splitlines():
		line = raw_line.strip()
		if not line or line.startswith('#'):
			continue
		if ':' not in line:
			raise ConfigError('config.yaml', raw_line, 'simple "key: value" entries')
		key, value = line.split(':', maxsplit=1)
		data[key.strip()] = value.strip()
	return data or None


def _validate_config_keys(path: Path, data: dict[str, Any]) -> None:
	allowed_keys = {'default_provider', 'lang'}
	unknown_keys = sorted(set(data) - allowed_keys)
	if unknown_keys:
		raise ConfigError(str(path), ', '.join(unknown_keys), 'supported config keys')


def _normalize_provider(value: Any) -> str | None:
	if value is None:
		return None
	if value in ALLOWED_PROVIDERS:
		return value
	raise ConfigError('default_provider', value, 'one of claude, codex')


def _normalize_lang(value: Any) -> str:
	if value is None:
		return 'auto'
	if value in ALLOWED_LANGUAGES:
		return value
	raise ConfigError('lang', value, 'one of auto, python, typescript')
