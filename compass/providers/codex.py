from __future__ import annotations

import asyncio

from compass.config import PROVIDER_TIMEOUT
from compass.providers.base import BaseProvider


class CodexProvider(BaseProvider):
	cli_binary = 'codex'

	async def call(self, prompt: str) -> str:
		proc = await asyncio.create_subprocess_exec(
			'codex',
			'exec',
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
			raise RuntimeError(f'codex CLI timed out after {PROVIDER_TIMEOUT}s')
		if proc.returncode != 0:
			raise RuntimeError(stderr.decode().strip() or 'codex CLI exited with non-zero status')
		return stdout.decode().strip()
