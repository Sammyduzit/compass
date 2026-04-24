from __future__ import annotations

from compass.providers.base import BaseProvider


class ClaudeProvider(BaseProvider):
	async def call(self, prompt: str) -> str:
		raise NotImplementedError
