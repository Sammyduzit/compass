from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from compass.config import CompassConfig, VALIDATION_RETRY_DELAY
from compass.errors import ProviderError, SchemaValidationError
from compass.paths import CompassPaths
from compass.providers.base import BaseProvider, get_provider


class AdapterBase(ABC):
	name: str

	def __init__(self, config: CompassConfig, paths: CompassPaths) -> None:
		self._config = config
		self._paths = paths
		self._provider: BaseProvider = get_provider(config)

	@abstractmethod
	async def run(self) -> None: ...

	def run_file_selector(self, criteria: dict[str, Any]) -> list[str]:
		# Stubbed until issue #20 (FileSelector) is ready.
		return []

	async def run_grep_ast(self, files: list[str]) -> str:
		if not files:
			return ''
		proc = await asyncio.create_subprocess_exec(
			'grep-ast',
			'--no-color',
			*files,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE,
		)
		stdout, _ = await proc.communicate()
		return stdout.decode()

	async def call_provider(self, prompt: str) -> str:
		try:
			return await self._provider.call(prompt)
		except RuntimeError as exc:
			raise ProviderError(self.name, self._config.provider or 'unknown', str(exc)) from exc

	async def validate_output(
		self,
		raw: str,
		validator: Callable[[str], Any],
		prompt: str,
	) -> Any:
		try:
			return validator(raw)
		except Exception as first_error:
			await asyncio.sleep(VALIDATION_RETRY_DELAY)
			retry_prompt = (
				f'{prompt}\n\n'
				f'Your previous response failed validation: {first_error}\n'
				f'Please correct it and try again.'
			)
			retry_raw = await self.call_provider(retry_prompt)
			try:
				return validator(retry_raw)
			except Exception as second_error:
				raise SchemaValidationError(self.name, str(second_error)) from second_error
