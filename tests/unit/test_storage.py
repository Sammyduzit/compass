"""Unit tests for Compass storage helpers."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from compass.storage.analysis_context_store import (
    read_analysis_context,
    write_analysis_context,
)
from compass.storage.output_writer import (
    write_adapter_output,
    write_output,
    write_rules_md,
    write_rules_yaml,
    write_summary_md,
)
from compass.storage.repo_state_hash import get_repo_head
from compass.storage.repo_state_store import (
    is_stale,
    read_repo_state,
    write_current_repo_state,
    write_repo_state,
)


@dataclass(frozen=True)
class FakeAnalysisContext:
    architecture: dict[str, object]
    patterns: dict[str, object]


def test_analysis_context_store_round_trips_dataclass(tmp_path: Path) -> None:
    context = FakeAnalysisContext(
        architecture={"file_scores": [{"path": "src/app.py", "centrality": 0.7}]},
        patterns={"naming": "snake_case"},
    )

    path = write_analysis_context(tmp_path, context)

    assert path == tmp_path / ".compass" / "analysis_context.json"
    assert read_analysis_context(tmp_path) == {
        "architecture": {"file_scores": [{"path": "src/app.py", "centrality": 0.7}]},
        "patterns": {"naming": "snake_case"},
    }


def test_repo_state_store_detects_missing_matching_and_changed_heads(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "compass.storage.repo_state_store.get_repo_head",
        lambda target_path: "abc123",
    )

    assert is_stale(tmp_path) is True

    write_current_repo_state(tmp_path)
    assert read_repo_state(tmp_path) == {"head": "abc123"}
    assert is_stale(tmp_path) is False

    monkeypatch.setattr(
        "compass.storage.repo_state_store.get_repo_head",
        lambda target_path: "def456",
    )
    assert is_stale(tmp_path) is True


def test_repo_state_hash_uses_git_rev_parse(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append({"args": args, "kwargs": kwargs})
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="abc123\n")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert get_repo_head(tmp_path) == "abc123"
    assert calls == [
        {
            "args": (["git", "rev-parse", "HEAD"],),
            "kwargs": {
                "cwd": tmp_path,
                "check": True,
                "capture_output": True,
                "text": True,
            },
        }
    ]


def test_output_writer_writes_known_adapter_outputs(tmp_path: Path) -> None:
    assert write_rules_md(tmp_path, "# Rules").read_text(encoding="utf-8") == "# Rules"
    assert (
        write_rules_yaml(tmp_path, "rules: []").read_text(encoding="utf-8")
        == "rules: []"
    )
    assert (
        write_summary_md(tmp_path, "# Summary").read_text(encoding="utf-8")
        == "# Summary"
    )
    assert (
        write_adapter_output(tmp_path, "summary", "Summary").read_text(encoding="utf-8")
        == "Summary"
    )

    assert (tmp_path / ".compass" / "output").is_dir()


def test_output_writer_rejects_nested_or_unknown_outputs(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must not include directories"):
        write_output(tmp_path, "../rules.yaml", "bad")

    with pytest.raises(ValueError, match="Unknown adapter output"):
        write_adapter_output(tmp_path, "unknown", "bad")


def test_repo_state_store_writes_expected_json(tmp_path: Path) -> None:
    path = write_repo_state(tmp_path, "abc123")

    assert path == tmp_path / ".compass" / "repo_state.json"
    assert json.loads(path.read_text(encoding="utf-8")) == {"head": "abc123"}
