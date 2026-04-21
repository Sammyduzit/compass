"""Logging helpers for Compass."""

from __future__ import annotations

import logging


LOGGER_NAME = "compass"


def configure_logging(level: str | int = logging.WARNING) -> None:
    """Configure simple console logging for CLI usage."""

    logging.basicConfig(
        level=_coerce_level(level),
        format="%(levelname)s: %(message)s",
    )


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger under the Compass namespace."""

    if name is None:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def _coerce_level(level: str | int) -> int:
    if isinstance(level, int):
        return level
    coerced = logging.getLevelName(level.upper())
    if isinstance(coerced, int):
        return coerced
    raise ValueError(f"Unknown log level: {level}")
