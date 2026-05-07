from __future__ import annotations

import asyncio

from compass.config import PROVIDER_TIMEOUT
from compass.providers.base import BaseProvider


class ClaudeProvider(BaseProvider):
	cli_binary = 'claude'

	async def call(self, prompt: str) -> str:
		proc = await asyncio.create_subprocess_exec(
			'claude',
			'-p',
			'-',
			stdin=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE,
		)
		try:
			stdout, stderr = await asyncio.wait_for(
				proc.communicate(input=prompt.encode()),
				timeout=PROVIDER_TIMEOUT,
			)
		except asyncio.TimeoutError:
			proc.kill()
			await proc.wait()
			raise RuntimeError(f'claude CLI timed out after {PROVIDER_TIMEOUT}s')
		if proc.returncode != 0:
			detail = (
				stderr.decode().strip()
				or stdout.decode().strip()
				or 'claude CLI exited with non-zero status'
			)
			raise RuntimeError(detail)
		return stdout.decode().strip()
