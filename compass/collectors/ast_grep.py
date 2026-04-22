import asyncio
import json
from pathlib import Path

from compass.collectors.base import BaseCollector
from compass.errors import CollectorError

PATTERNS: dict[str, list[tuple[str, str]]] = {
	'error_handling': [
		('except $_ as $_:', 'python'),
		('except $_:', 'python'),
	],
	'decorators': [
		('@$DECORATOR', 'python'),
	],
	'naming': [
		('def $NAME($$$)', 'python'),
		('class $NAME($$$)', 'python'),
	],
}


class AstGrepCollector(BaseCollector[dict[str, list[str]]]):
	async def collect(self, target_path: Path) -> dict[str, list[str]]:
		results: dict[str, list[str]] = {key: [] for key in PATTERNS}

		for category, patterns in PATTERNS.items():
			for pattern, lang in patterns:
				proc = await asyncio.create_subprocess_exec(
					'ast-grep',
					'--pattern',
					pattern,
					'--lang',
					lang,
					'--json',
					str(target_path),
					stdout=asyncio.subprocess.PIPE,
					stderr=asyncio.subprocess.PIPE,
				)
				stdout, stderr = await proc.communicate()
				if proc.returncode != 0:
					raise CollectorError(
						'ast-grep failed or is not installed. Run: brew install ast-grep'
					)

				output = stdout.decode()
				data = json.loads(output)
				for item in data:
					results[category].append(item['text'])
		return results
