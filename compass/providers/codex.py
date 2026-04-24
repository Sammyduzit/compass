from __future__ import annotations

from compass.providers.base import BaseProvider


class CodexProvider(BaseProvider):
	async def call(self, prompt: str) -> str:
		raise NotImplementedError
