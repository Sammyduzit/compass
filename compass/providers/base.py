from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from compass.config import CompassConfig
from compass.errors import ConfigError


class BaseProvider(ABC):
	cli_binary: ClassVar[str]

	@abstractmethod
	async def call(self, prompt: str) -> str: ...


def get_provider(config: CompassConfig) -> BaseProvider:

	if not config.provider or config.provider not in PROVIDER_REGISTRY:
		raise ConfigError(
			'provider',
			config.provider,
			f'one of: {", ".join(PROVIDER_REGISTRY)}',
		)

	return PROVIDER_REGISTRY[config.provider]()


from compass.providers.claude import ClaudeProvider  # noqa: E402
from compass.providers.codex import CodexProvider  # noqa: E402

PROVIDER_REGISTRY = {
	'claude': ClaudeProvider,
	'codex': CodexProvider,
}
