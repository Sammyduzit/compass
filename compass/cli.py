"""Thin CLI entry point for Compass."""

from __future__ import annotations

import argparse

from compass.config import CompassConfig
from compass.log import configure_logging


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog='compass',
		description='Analyze a repository and generate Compass outputs.',
	)
	parser.add_argument('target_path', nargs='?', help='Path to the target repository.')
	parser.add_argument(
		'--adapters',
		default='rules',
		help='Comma-separated adapters to run, or "all". Defaults to "rules".',
	)
	parser.add_argument(
		'--provider',
		choices=('claude', 'codex'),
		help='LLM provider to use. Falls back to config.yaml when omitted.',
	)
	parser.add_argument(
		'--lang',
		default='auto',
		choices=('auto', 'python', 'typescript'),
		help='Target language. Defaults to "auto".',
	)
	parser.add_argument(
		'--reanalyze',
		action='store_true',
		help='Rebuild analysis context instead of reusing cached state.',
	)
	parser.add_argument(
		'--log-level',
		default='WARNING',
		choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
		help='Console log level. Defaults to "WARNING".',
	)
	return parser


def parse_adapters(value: str) -> list[str]:
	return [adapter.strip() for adapter in value.split(',') if adapter.strip()]


def main(argv: list[str] | None = None) -> int:
	parser = build_parser()
	args = parser.parse_args(argv)
	configure_logging(args.log_level)

	if args.target_path is None:
		parser.print_help()
		return 0

	CompassConfig(
		target_path=args.target_path,
		adapters=parse_adapters(args.adapters),
		provider=args.provider,
		lang=args.lang,
		reanalyze=args.reanalyze,
	)
	parser.exit(2, 'Compass runner is not implemented yet.\n')
	return 2
