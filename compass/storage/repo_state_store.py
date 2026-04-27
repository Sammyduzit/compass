"""Read and write ``.compass/repo_state.json``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from compass.paths import compass_paths
from compass.storage.repo_state_hash import get_repo_head


HEAD_KEY = 'head'


def read_repo_state(target_path: str | Path) -> dict[str, Any] | None:
	path = compass_paths(target_path).repo_state
	if not path.exists():
		return None
	with path.open(encoding='utf-8') as file:
		data = json.load(file)
	if not isinstance(data, dict):
		raise ValueError('repo_state.json must contain a JSON object')
	return data


def write_repo_state(target_path: str | Path, head: str) -> Path:
	path = compass_paths(target_path).repo_state
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open('w', encoding='utf-8') as file:
		json.dump({HEAD_KEY: head}, file, indent=2, sort_keys=True)
		file.write('\n')
	return path


def write_current_repo_state(target_path: str | Path) -> Path:
	return write_repo_state(target_path, get_repo_head(target_path))


def is_stale(target_path: str | Path) -> bool:
	stored_state = read_repo_state(target_path)
	if stored_state is None:
		return True
	stored_head = stored_state.get(HEAD_KEY)
	if not isinstance(stored_head, str) or stored_head == '':
		return True
	return stored_head != get_repo_head(target_path)
