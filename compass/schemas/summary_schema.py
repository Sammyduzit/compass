"""
summary_schema.py — Validates summary.json output from SummaryAdapter.

Generated alongside summary.md in the same adapter run. The JSON is the
data layer; summary.md is one rendering of it.

Schema (from prompts/templates/summary.md — JSON Output section):

    {
      "repo_name": str,
      "generated_at": str,          # ISO 8601 timestamp
      "what_it_does": str,
      "read_first": [
        { "path": str, "reason": str }
      ],
      "stable": [
        { "path": str, "note": str }
      ],
      "hotspots": [
        { "path": str, "note": str }
      ],
      "clusters": [
        {
          "id": int,
          "summary": str,
          "files": [str],
          "coupling_pairs": [[str, str]]
        }
      ]
    }

All list fields are required. Empty arrays [] are valid — use them when
a section has no content. No field may be omitted.

Usage:
    from compass.schemas.summary_schema import validate_summary

    result = validate_summary(parsed_json)
    if not result.valid:
        for error in result.errors:
            print(error)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator, model_validator


# ---------------------------------------------------------------------------
# Schema models
# ---------------------------------------------------------------------------

class ReadFirstEntry(BaseModel):
    path: str
    reason: str

    @field_validator("path", "reason")
    @classmethod
    def no_empty_strings(cls, v: str, info: Any) -> str:
        if not v.strip():
            raise ValueError(f"Field '{info.field_name}' must not be empty.")
        return v


class FileNote(BaseModel):
    """Shared shape for stable[] and hotspots[] entries."""
    path: str
    note: str

    @field_validator("path", "note")
    @classmethod
    def no_empty_strings(cls, v: str, info: Any) -> str:
        if not v.strip():
            raise ValueError(f"Field '{info.field_name}' must not be empty.")
        return v


class CouplingPair(BaseModel):
    """Two file paths that co-change. Validated as a two-element list."""
    files: list[str]

    @model_validator(mode="before")
    @classmethod
    def from_list(cls, v: Any) -> dict[str, Any]:
        if isinstance(v, list):
            return {"files": v}
        return v

    @field_validator("files")
    @classmethod
    def exactly_two_paths(cls, v: list[str]) -> list[str]:
        if len(v) != 2:
            raise ValueError(
                f"Each coupling pair must contain exactly two file paths. "
                f"Got {len(v)}."
            )
        for path in v:
            if not path.strip():
                raise ValueError("File paths in coupling pairs must not be empty.")
        return v


class Cluster(BaseModel):
    id: int
    summary: str
    files: list[str]
    coupling_pairs: list[CouplingPair]

    @field_validator("summary")
    @classmethod
    def no_empty_summary(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Cluster 'summary' must not be empty.")
        return v

    @field_validator("files")
    @classmethod
    def files_not_empty_strings(cls, v: list[str]) -> list[str]:
        for path in v:
            if not path.strip():
                raise ValueError("File paths in cluster 'files' must not be empty.")
        return v


class SummaryOutput(BaseModel):
    repo_name: str
    generated_at: str
    what_it_does: str
    read_first: list[ReadFirstEntry]
    stable: list[FileNote]
    hotspots: list[FileNote]
    clusters: list[Cluster]

    @field_validator("repo_name", "what_it_does")
    @classmethod
    def no_empty_strings(cls, v: str, info: Any) -> str:
        if not v.strip():
            raise ValueError(f"Field '{info.field_name}' must not be empty.")
        return v

    @field_validator("generated_at")
    @classmethod
    def valid_iso_timestamp(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field 'generated_at' must not be empty.")
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(
                f"Field 'generated_at' must be a valid ISO 8601 timestamp. "
                f"Got: '{v}'."
            )
        return v


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

def validate_summary(data: dict[str, Any]) -> ValidationResult:
    """
    Validate a parsed summary.json dict against the locked Compass schema.

    All list fields (read_first, stable, hotspots, clusters) are required
    but may be empty arrays. No field may be omitted.

    Args:
        data: The result of json.loads() on a summary.json file.

    Returns:
        ValidationResult with valid=True and empty errors list on success,
        or valid=False with a list of human-readable error messages on failure.

    Example:
        import json
        from compass.schemas.summary_schema import validate_summary

        with open(".compass/output/summary.json") as f:
            data = json.load(f)

        result = validate_summary(data)
        if not result.valid:
            for error in result.errors:
                print(f"  - {error}")
    """
    try:
        SummaryOutput.model_validate(data)
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
        location = " → ".join(str(part) for part in error["loc"]) if error["loc"] else "root"
        message = error["msg"]
        errors.append(f"{location}: {message}")
    return errors
