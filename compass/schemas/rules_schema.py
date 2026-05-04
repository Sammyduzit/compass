"""
rules_schema.py — Validates rules.yaml output from RulesAdapter.

The locked two-level schema (from PROJECT_RULES.md):

    clusters:
      - name: str
        context: str
        golden_file: str
        rules:
          - id: str         # kebab-case prefix + two-digit number, e.g. "err-01"
            rule: str
            why: str
            example: str

Usage:
    from compass.schemas.rules_schema import validate_rules

    result = validate_rules(parsed_yaml)
    if not result.valid:
        for error in result.errors:
            print(error)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, field_validator, model_validator


# ---------------------------------------------------------------------------
# Schema models
# ---------------------------------------------------------------------------


class Rule(BaseModel):
	id: str
	rule: str
	why: str
	example: str

	@field_validator('id')
	@classmethod
	def id_format(cls, v: str) -> str:
		pattern = r'^[a-z][a-z0-9]*(-[a-z0-9]+)*-\d{2}$'
		if not re.match(pattern, v):
			raise ValueError(
				f"Rule id '{v}' does not match expected format. "
				'Expected kebab-case prefix followed by a two-digit number '
				"(e.g. 'err-01', 'phase-boundary-02')."
			)
		return v

	@field_validator('rule', 'why', 'example')
	@classmethod
	def no_empty_strings(cls, v: str, info: Any) -> str:
		if not v.strip():
			raise ValueError(f"Field '{info.field_name}' must not be empty.")
		return v


class Cluster(BaseModel):
	name: str
	context: str
	golden_file: str
	rules: list[Rule]

	@field_validator('name', 'context', 'golden_file')
	@classmethod
	def no_empty_strings(cls, v: str, info: Any) -> str:
		if not v.strip():
			raise ValueError(f"Field '{info.field_name}' must not be empty.")
		return v

	@field_validator('rules')
	@classmethod
	def at_least_one_rule(cls, v: list[Rule]) -> list[Rule]:
		if not v:
			raise ValueError('Each cluster must contain at least one rule.')
		return v


class RulesOutput(BaseModel):
	clusters: list[Cluster]

	@field_validator('clusters')
	@classmethod
	def at_least_one_cluster(cls, v: list[Cluster]) -> list[Cluster]:
		if not v:
			raise ValueError('rules.yaml must contain at least one cluster.')
		return v

	@model_validator(mode='after')
	def rule_ids_unique(self) -> RulesOutput:
		seen: set[str] = set()
		duplicates: list[str] = []
		for cluster in self.clusters:
			for rule in cluster.rules:
				if rule.id in seen:
					duplicates.append(rule.id)
				seen.add(rule.id)
		if duplicates:
			raise ValueError(
				f'Rule ids must be unique across all clusters. '
				f'Duplicates found: {", ".join(duplicates)}'
			)
		return self


# ---------------------------------------------------------------------------
# Validation result
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
	valid: bool
	errors: list[str] = field(default_factory=list)

	def __bool__(self) -> bool:
		return self.valid


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def validate_rules(data: dict[str, Any]) -> ValidationResult:
	"""
	Validate a parsed rules.yaml dict against the locked Compass schema.

	Args:
	    data: The result of yaml.safe_load() on a rules.yaml file.

	Returns:
	    ValidationResult with valid=True and empty errors list on success,
	    or valid=False with a list of human-readable error messages on failure.

	Example:
	    import yaml
	    from compass.schemas.rules_schema import validate_rules

	    with open(".compass/output/rules.yaml") as f:
	        data = yaml.safe_load(f)

	    result = validate_rules(data)
	    if not result.valid:
	        for error in result.errors:
	            print(f"  - {error}")
	"""
	try:
		RulesOutput.model_validate(data)
		return ValidationResult(valid=True)
	except Exception as exc:
		errors = _extract_errors(exc)
		return ValidationResult(valid=False, errors=errors)


def _extract_errors(exc: Exception) -> list[str]:
	"""
	Convert a pydantic ValidationError into a flat list of readable strings.
	Each string names the location in the document and what went wrong.
	"""
	from pydantic import ValidationError

	if not isinstance(exc, ValidationError):
		return [str(exc)]

	errors: list[str] = []
	for error in exc.errors():
		location = ' → '.join(str(part) for part in error['loc']) if error['loc'] else 'root'
		message = error['msg']
		errors.append(f'{location}: {message}')
	return errors
