from __future__ import annotations

from abc import ABC, abstractmethod

from compass.config import CompassConfig
from compass.errors import ConfigError


class BaseProvider(ABC):
    @abstractmethod
    async def call(self, prompt: str) -> str: ...


def get_provider(config: CompassConfig) -> BaseProvider:
    from compass.providers.claude import ClaudeProvider
    from compass.providers.codex import CodexProvider

    registry: dict[str, type[BaseProvider]] = {
        "claude": ClaudeProvider,
        "codex": CodexProvider,
    }

    if not config.provider or config.provider not in registry:
        raise ConfigError(
            "provider",
            config.provider,
            f'one of: {", ".join(registry)}',
        )

    return registry[config.provider]()
