"""Maps CompassError subclasses to HTTP responses."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from compass.errors import (
	AdapterError,
	CollectorError,
	CompassError,
	ConfigError,
	PrerequisiteError,
)


async def compass_error_handler(request: Request, exc: CompassError) -> JSONResponse:
	if isinstance(exc, ConfigError):
		status = 422
	elif isinstance(exc, PrerequisiteError):
		status = 503
	elif isinstance(exc, (CollectorError, AdapterError)):
		status = 500
	else:
		status = 500

	return JSONResponse(status_code=status, content={'detail': str(exc)})
