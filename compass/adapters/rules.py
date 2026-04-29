from __future__ import annotations

import asyncio

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
	
	async def build_prompt(self, context: AnalysisContext, skeletons: str, repomix_bodies: str, lang: str) -> str:
		template = load_template('extract_rules', lang)
		input_dict = {
			"domain": "",
			"files": [{}],
			"git_patterns": {
				"hotspots": context.git_patterns.hotspots,
				"stable_files": context.git_patterns.stable_files,
				"coupling_clusters": context.git_patterns.coupling_clusters,
			},
			"docs": context.docs,
			"golden_files": [{}]
		}