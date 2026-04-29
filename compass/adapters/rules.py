from __future__ import annotations

import asyncio
import json
from pathlib import Path

from compass.adapters.base import AdapterBase
from compass.domain.analysis_context import AnalysisContext
from compass.prompts.loader import load_template


class RulesAdapter(AdapterBase):
	name = 'rules'

	async def run(self) -> None:
		pass

	async def _run_repomix(self, files: list[str]) -> str:
		if not files:
			return ''
		proc = await asyncio.create_subprocess_exec(
			'repomix',
			'--compress',
			*files,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE,
		)
		stdout, _ = await proc.communicate()
		return stdout.decode()

	async def build_prompt(
		self, context: AnalysisContext, skeletons: str, repomix_bodies: str, domain: str, lang: str
	) -> str:
		template = load_template('extract_rules', lang)
		top_files = sorted(
			context.architecture.file_scores, key=lambda s: s.centrality, reverse=True
		)[:10]
		input_dict = {
			'file_content': repomix_bodies,
			'skeleton': skeletons,
			'ast_patterns': context.patterns,
			'domain': domain,
			'files': [
				{
					'path': score.path,
					'churn': score.churn,
					'age_days': score.age,
					'centrality': score.centrality,
					'coupling_pairs': list(score.coupling_pairs),
				}
				for score in context.architecture.file_scores
			],
			'git_patterns': {
				'hotspots': context.git_patterns.hotspots,
				'stable_files': context.git_patterns.stable_files,
				'coupling_clusters': context.git_patterns.coupling_clusters,
			},
			'docs': context.docs,
			'golden_files': [
				{'path': score.path, 'content': Path(score.path).read_text()} for score in top_files
			],
		}

		return f'{template}\n\n## Input\n\n```json\n{json.dumps(input_dict, indent=2)}\n```'
