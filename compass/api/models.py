"""Request and response models for the Compass API."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from compass.schemas.rules_schema import RulesOutput
from compass.schemas.summary_schema import SummaryOutput


class AdapterName(str, Enum):
	rules = 'rules'
	summary = 'summary'


class RunRequest(BaseModel):
	target_path: str
	adapters: list[AdapterName] = Field(min_length=1)
	provider: str | None = None
	lang: str = 'auto'
	reanalyze: bool = False


class RunResponse(BaseModel):
	output_paths: list[str]


class SummaryOutputResponse(BaseModel):
	adapter: AdapterName = AdapterName.summary
	output_path: str
	data: SummaryOutput


class RulesOutputResponse(BaseModel):
	adapter: AdapterName = AdapterName.rules
	output_path: str
	data: RulesOutput
