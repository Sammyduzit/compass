"""Request and response models for the Compass API."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel

AdaptersName = Literal["rules", "summary"]

class RunRequest(BaseModel):
    target_path: str
    adapters: list[AdaptersName]
    provider: Literal ["claude", "codex"] | None = None
    lang: Literal["auto", "python", "typescript"] = "auto"
    reanalyze: bool = False


class RunResponse(BaseModel):
    output_paths: list[str]
