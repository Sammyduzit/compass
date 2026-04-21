"""Shared Compass configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CompassConfig:
    """Configuration passed unchanged from the CLI boundary into the runner."""

    target_path: str
    adapters: list[str] = field(default_factory=lambda: ["rules"])
    provider: str | None = None
    lang: str = "auto"
    reanalyze: bool = False
