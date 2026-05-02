from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any

import yaml

from compass.adapters.base import AdapterBase
from compass.domain.analysis_context import AnalysisContext
from compass.domain.file_score import FileScore
from compass.language_detection import detect
from compass.prompts.loader import load_template
from compass.schemas.rules_schema import RulesOutput
from compass.storage.analysis_context_store import read_analysis_context
from compass.storage.output_writer import write_rules_md, write_rules_yaml


class RulesAdapter(AdapterBase):
	name = 'rules'

	def _top_files(self, context: AnalysisContext) -> list[FileScore]:

		return sorted(context.architecture.file_scores, key=lambda s: s.centrality, reverse=True)[
			:10
		]

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

	def build_prompt(
		self, context: AnalysisContext, skeletons: str, repomix_bodies: str, domain: str, lang: str
	) -> str:
		template = load_template('extract_rules', lang)
		top_files = self._top_files(context)
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

	def build_reconciliation_prompt(
		self, context: AnalysisContext, extracted_rules: str, domain: str, lang: str
	) -> str:
		template = load_template('reconciliation', lang)
		top_files = self._top_files(context)
		input_dict = {
			'mode': 'per-batch',
			'domain': domain,
			'extracted_rules': extracted_rules,
			'golden_files': [
				{'path': score.path, 'content': Path(score.path).read_text()} for score in top_files
			],
			'docs': context.docs,
		}
		return f'{template}\n\n## Input\n\n```json\n{json.dumps(input_dict, indent=2)}\n```'

	def parse_reconciliation_output(self, raw_llm_output: str) -> str:
		pattern = r'### FINAL YAML OUTPUT ###\s*```(?:yaml)?\n(.*?)```'
		match = re.search(pattern, raw_llm_output, re.DOTALL | re.IGNORECASE)
		if not match:
			raise ValueError(
				"LLM Output missing strict section header '### FINAL YAML OUTPUT ###' or yaml fence."
			)
		return match.group(1).strip()

	async def run(self) -> None:
		context = read_analysis_context(self._paths.target_path)
		language = detect(self._paths.target_path, self._config.lang)
		files = self.run_file_selector({})

		skeletons, repomix_bodies = await asyncio.gather(
			self.run_grep_ast(files),
			self._run_repomix(files),
		)
		repo_name = Path(self._paths.target_path).name
		extraction_prompt = self.build_prompt(
			context, skeletons, repomix_bodies, repo_name, language
		)
		rules_md = await self.call_provider(extraction_prompt)
		write_rules_md(self._paths.target_path, rules_md)

		reconciliation_prompt = self.build_reconciliation_prompt(
			context, rules_md, repo_name, language
		)
		final_rules_md = await self.call_provider(reconciliation_prompt)
		write_rules_md(self._paths.target_path, final_rules_md)

		yaml_str = self.parse_reconciliation_output(final_rules_md)

		def validator(raw: str) -> Any:
			return RulesOutput.model_validate(yaml.safe_load(raw))

		validation_result = await self.validate_output(yaml_str, validator, reconciliation_prompt)
		write_rules_yaml(self._paths.target_path, yaml.dump(validation_result.model_dump()))
