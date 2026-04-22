"""Compute repository fingerprints for staleness checks."""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_repo_head(target_path: str | Path) -> str:
    """Return the current git HEAD SHA for ``target_path``."""

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=Path(target_path),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
