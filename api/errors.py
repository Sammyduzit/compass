"""Maps CompassError subclasses to HTTP responses."""

from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from compass.errors import (
    AdapterError,
    CollectorError,
    CompassError,
    ConfigError,
    PrerequisiteError,
    ProviderError,
    RepomixError,
    SchemaValidationError,
    SkeletonError,
    TemplateNotFoundError,
)


def _status_for_error(exc: CompassError) -> int:
    if isinstance(exc, (ConfigError, PrerequisiteError)):
        return 422
    if isinstance(exc, (ProviderError, SchemaValidationError)):
        return 502
    if isinstance(exc, RepomixError):
        return 503
    if isinstance(exc, (CollectorError, AdapterError, SkeletonError, TemplateNotFoundError)):
        return 500
    logging.warning("Unbekannte CompassError-Subklasse: %s", type(exc).__name__)
    return 500


async def compass_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, CompassError)
    return JSONResponse(status_code=_status_for_error(exc), content={'detail': str(exc)})
