"""Unit tests for Compass prerequisite checks."""

from __future__ import annotations

import io
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from compass.errors import PrerequisiteError
from compass.prerequisites import check


def test_check_raises_for_missing_python_modules(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	monkeypatch.setattr('compass.prerequisites.which', lambda name: '/usr/bin/tool')

	def fake_find_spec(module_name: str) -> object | None:
		if module_name == 'grep_ast':
			return None
		return SimpleNamespace(name=module_name)

	monkeypatch.setattr('compass.prerequisites.importlib.util.find_spec', fake_find_spec)

	with pytest.raises(PrerequisiteError, match='grep_ast'):
		check(tmp_path)


@pytest.mark.parametrize(
	('binary_name', 'expected_message'),
	[
		('ast-grep', 'ast-grep'),
		('repomix', 'repomix'),
		('git', 'git'),
	],
)
def test_check_raises_for_missing_required_binaries(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
	binary_name: str,
	expected_message: str,
) -> None:
	monkeypatch.setattr(
		'compass.prerequisites.importlib.util.find_spec',
		lambda module_name: SimpleNamespace(name=module_name),
	)

	def fake_which(name: str) -> str | None:
		if binary_name == 'ast-grep' and name in {'ast-grep', 'sg'}:
			return None
		if name == binary_name:
			return None
		return f'/usr/bin/{name}'

	monkeypatch.setattr('compass.prerequisites.which', fake_which)
	monkeypatch.setattr(
		'compass.prerequisites._find_codebase_memory_mcp',
		lambda: tmp_path / '.compass' / 'bin' / 'codebase-memory-mcp',
	)

	with pytest.raises(PrerequisiteError, match=expected_message):
		check(tmp_path)


def test_check_requires_at_least_one_provider(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	monkeypatch.setattr(
		'compass.prerequisites.importlib.util.find_spec',
		lambda module_name: SimpleNamespace(name=module_name),
	)

	def fake_which(name: str) -> str | None:
		if name in {'claude', 'codex'}:
			return None
		return f'/usr/bin/{name}'

	monkeypatch.setattr('compass.prerequisites.which', fake_which)
	monkeypatch.setattr(
		'compass.prerequisites._find_codebase_memory_mcp',
		lambda: tmp_path / '.compass' / 'bin' / 'codebase-memory-mcp',
	)

	with pytest.raises(PrerequisiteError, match='provider CLI'):
		check(tmp_path)


def test_check_passes_when_one_provider_is_available(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	monkeypatch.setattr(
		'compass.prerequisites.importlib.util.find_spec',
		lambda module_name: SimpleNamespace(name=module_name),
	)

	def fake_which(name: str) -> str | None:
		if name == 'claude':
			return '/usr/local/bin/claude'
		if name == 'codex':
			return None
		return f'/usr/bin/{name}'

	monkeypatch.setattr('compass.prerequisites.which', fake_which)
	monkeypatch.setattr(
		'compass.prerequisites._find_codebase_memory_mcp',
		lambda: tmp_path / '.compass' / 'bin' / 'codebase-memory-mcp',
	)

	check(tmp_path)


def test_check_auto_downloads_codebase_memory_mcp_when_missing(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	home_dir = tmp_path / 'home'

	monkeypatch.setattr('compass.prerequisites.Path.home', lambda: home_dir)
	monkeypatch.setattr(
		'compass.prerequisites.importlib.util.find_spec',
		lambda module_name: SimpleNamespace(name=module_name),
	)

	def fake_which(name: str) -> str | None:
		if name == 'codebase-memory-mcp':
			return None
		return f'/usr/bin/{name}'

	monkeypatch.setattr('compass.prerequisites.which', fake_which)
	monkeypatch.setattr('compass.prerequisites.platform.system', lambda: 'Darwin')
	monkeypatch.setattr('compass.prerequisites.platform.machine', lambda: 'arm64')
	monkeypatch.setattr(
		'compass.prerequisites.urlopen',
		lambda url, timeout: io.BytesIO(_build_codebase_memory_archive()),
	)

	check(tmp_path)

	binary_path = home_dir / '.compass' / 'bin' / 'codebase-memory-mcp'
	assert binary_path.exists()
	assert binary_path.read_bytes() == b'#!/bin/sh\nexit 0\n'


def test_check_raises_when_codebase_memory_download_fails(
	tmp_path: Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	home_dir = tmp_path / 'home'

	monkeypatch.setattr('compass.prerequisites.Path.home', lambda: home_dir)
	monkeypatch.setattr(
		'compass.prerequisites.importlib.util.find_spec',
		lambda module_name: SimpleNamespace(name=module_name),
	)

	def fake_which(name: str) -> str | None:
		if name == 'codebase-memory-mcp':
			return None
		return f'/usr/bin/{name}'

	monkeypatch.setattr('compass.prerequisites.which', fake_which)
	monkeypatch.setattr('compass.prerequisites.platform.system', lambda: 'Darwin')
	monkeypatch.setattr('compass.prerequisites.platform.machine', lambda: 'arm64')

	def fake_urlopen(url: str, timeout: int) -> io.BytesIO:
		raise OSError('network down')

	monkeypatch.setattr('compass.prerequisites.urlopen', fake_urlopen)

	with pytest.raises(PrerequisiteError, match='auto-download failed'):
		check(tmp_path)


def _build_codebase_memory_archive() -> bytes:
	buffer = io.BytesIO()
	with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
		payload = b'#!/bin/sh\nexit 0\n'
		info = tarfile.TarInfo(name='codebase-memory-mcp')
		info.size = len(payload)
		archive.addfile(info, io.BytesIO(payload))
	return buffer.getvalue()
