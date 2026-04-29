from __future__ import annotations

import json
import re

from compass.adapters.base import AdapterBase
from compass.domain.analysis_context import AnalysisContext
from compass.prompts.loader import load_template
from compass.schemas.summary_schema import validate_summary
from compass.skeleton import render_skeletons
from compass.storage.analysis_context_store import read_analysis_context

_JSON_BLOCK = re.compile(r'## JSON Output.*?```json\s*(\{.*?\})\s*```', re.DOTALL)


def _validate_summary_response(raw: str) -> tuple[str, dict]:
	match = _JSON_BLOCK.search(raw)
	if match is None:
		raise ValueError('No JSON block found in response')
	try:
		data = json.loads(match.group(1))
	except json.JSONDecodeError as exc:
		raise ValueError(f'Invalid JSON in response: {exc}') from exc
	result = validate_summary(data)
	if not result:
		errors = '; '.join(result.errors)
		raise ValueError(f'summary.json validation failed: {errors}')
	md_text = raw[: match.start()].strip()
	if not md_text:
		raise ValueError('No markdown content found in response')
	return md_text, data


class SummaryAdapter(AdapterBase):
	name = 'summary'

	@staticmethod
	def _read_readme(target_path: str) -> str | None:
		from pathlib import Path

		for name in ('README.md', 'README.rst', 'README.txt', 'README'):
			candidate = Path(target_path) / name
			if candidate.exists():
				return candidate.read_text(encoding='utf-8', errors='replace')
		return None

	def build_prompt(self, context: AnalysisContext, lang: str) -> str:
		template = load_template('summary', lang)
		skeletons = render_skeletons([fs.path for fs in context.architecture.file_scores])
		repo_input = {
			'repo_name': self._paths.target_path.name,
			'language': lang,
			'readme': self._read_readme(str(self._paths.target_path)),
			'files': [
				{
					'path': fs.path,
					'skeleton': skeletons.get(fs.path),
					'churn': fs.churn,
					'age_days': fs.age,
					'centrality': fs.centrality,
					'cluster_id': fs.cluster_id,
				}
				for fs in context.architecture.file_scores
			],
			'git_patterns': {
				'hotspots': context.git_patterns.hotspots,
				'stable_files': context.git_patterns.stable_files,
				'coupling_clusters': context.git_patterns.coupling_clusters,
			},
			'architecture': {
				'clusters': [
					{'id': c.id, 'files': list(c.files)} for c in context.architecture.clusters
				],
				'coupling_pairs': [
					[pair.file_a, pair.file_b] for pair in context.architecture.coupling_pairs
				],
			},
			'skeletons': skeletons,
		}
		return f'{template}\n\n```json\n{json.dumps(repo_input, indent=2)}\n```'

	async def run(self) -> None:
		context = read_analysis_context(self._paths.target_path)
		lang = self._config.lang if self._config.lang != 'auto' else 'generic'
		prompt = self.build_prompt(context, lang)
		raw = await self.call_provider(prompt)
		md_text, json_data = await self.validate_output(raw, _validate_summary_response, prompt)
		self._paths.output_dir.mkdir(parents=True, exist_ok=True)
		self._paths.summary_md.write_text(md_text, encoding='utf-8')
		(self._paths.output_dir / 'summary.json').write_text(
			json.dumps(json_data, indent=2), encoding='utf-8'
		)
