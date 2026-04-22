"""Write adapter output artifacts under ``.compass/output``."""

from __future__ import annotations

from pathlib import Path

from compass.paths import compass_paths


def write_output(target_path: str | Path, filename: str, content: str) -> Path:
    """Write an output artifact beneath ``.compass/output``."""

    if "/" in filename or "\\" in filename:
        raise ValueError("Output filename must not include directories")

    output_dir = compass_paths(target_path).output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def write_rules_md(target_path: str | Path, content: str) -> Path:
    return write_output(target_path, "rules.md", content)


def write_rules_yaml(target_path: str | Path, content: str) -> Path:
    return write_output(target_path, "rules.yaml", content)


def write_summary_md(target_path: str | Path, content: str) -> Path:
    return write_output(target_path, "summary.md", content)


def write_adapter_output(
    target_path: str | Path, adapter_name: str, content: str
) -> Path:
    """Write the canonical artifact for an adapter."""

    filenames = {
        "rules": "rules.yaml",
        "summary": "summary.md",
    }
    try:
        filename = filenames[adapter_name]
    except KeyError as error:
        raise ValueError(f"Unknown adapter output: {adapter_name}") from error
    return write_output(target_path, filename, content)
