from __future__ import annotations


class CompassError(Exception):
	"""Base exception for all Compass user-facing errors."""


class ConfigError(CompassError):
	"""Raised when configuration input is invalid."""

	def __init__(self, field: str, value: object, expected: str) -> None:
		super().__init__(f"Invalid config value for '{field}': {value!r}. Expected: {expected}.")


class PrerequisiteError(CompassError):
	"""Raised when a required tool or environment dependency is missing."""

	def __init__(self, tool: str, reason: str, install_instructions: str) -> None:
		super().__init__(
			f'Missing prerequisite: {tool}. {reason} Install with: {install_instructions}.'
		)


class CollectorError(CompassError):
	"""Raised when Phase 1 collection fails."""

	def __init__(self, collector: str, reason: str) -> None:
		super().__init__(f"Collector '{collector}' failed: {reason}")


class SkeletonError(CompassError):
	"""Raised when skeleton rendering fails."""

	def __init__(self, reason: str) -> None:
		super().__init__(f'Skeleton render failed: {reason}')


class AdapterError(CompassError):
	"""Raised when Phase 2 adapter execution fails."""

	def __init__(self, adapter: str, reason: str) -> None:
		super().__init__(f"Adapter '{adapter}' failed: {reason}")


class ProviderError(AdapterError):
	"""Raised when a provider subprocess fails or times out."""

	def __init__(self, adapter: str, provider: str, reason: str) -> None:
		super().__init__(adapter, f"provider '{provider}' error: {reason}")


class SchemaValidationError(AdapterError):
	"""Raised when provider output does not match the expected schema."""

	def __init__(self, adapter: str, reason: str) -> None:
		super().__init__(adapter, f'schema validation failed: {reason}')


class TemplateNotFoundError(CompassError):
	"""Raised when an unknown prompt template name is requested."""

	def __init__(self, template: str, available: list[str]) -> None:
		super().__init__(f'Unknown prompt template: {template!r}. Available: {available}')
