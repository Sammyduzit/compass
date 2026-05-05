"""Request and response models for the Compass API."""

from __future__ import annotations

from pydantic import BaseModel
from compass.schemas.rules_schema import RulesOutput


class RunRequest(BaseModel):
    target_path: str
    adapters: list[str]
    provider: str | None = None
    lang: str = "auto"
    reanalyze: bool = False


class RunResponse(BaseModel):
    output_paths: list[str]
