from __future__ import annotations

import shutil

from compass.errors import PrerequisiteError


CODEBASE_MEMORY_MCP = 'codebase-memory-mcp'
CODEBASE_MEMORY_MCP_RELEASES: Final[dict[tuple[str, str], str]] = {
	('Darwin', 'arm64'): (
		'https://github.com/DeusData/codebase-memory-mcp/releases/latest/download/'
		'codebase-memory-mcp-darwin-arm64.tar.gz'
	),
	('Darwin', 'x86_64'): (
		'https://github.com/DeusData/codebase-memory-mcp/releases/latest/download/'
		'codebase-memory-mcp-darwin-amd64.tar.gz'
	),
	('Linux', 'aarch64'): (
		'https://github.com/DeusData/codebase-memory-mcp/releases/latest/download/'
		'codebase-memory-mcp-linux-arm64.tar.gz'
	),
	('Linux', 'arm64'): (
		'https://github.com/DeusData/codebase-memory-mcp/releases/latest/download/'
		'codebase-memory-mcp-linux-arm64.tar.gz'
	),
	('Linux', 'x86_64'): (
		'https://github.com/DeusData/codebase-memory-mcp/releases/latest/download/'
		'codebase-memory-mcp-linux-amd64.tar.gz'
	),
}


def check() -> None:
	"""Validate all Compass runtime prerequisites."""

	_require_python_module(
		'grep_ast',
		install_instructions='pip install -e .',
		reason='The grep_ast Python package is required for Phase 2 skeleton rendering.',
	)
	_require_python_module(
		'mcp',
		install_instructions='pip install -e .',
		reason='The MCP Python SDK is required for the import graph collector.',
	)
	_require_binary(
		tool='ast-grep',
		candidates=('ast-grep', 'sg'),
		install_instructions='brew install ast-grep  or  cargo install ast-grep',
		reason='The ast-grep CLI is required for structural pattern extraction.',
	)
	_require_binary(
		tool='repomix',
		candidates=('repomix',),
		install_instructions='brew install repomix  or  npm install -g repomix',
		reason='The repomix CLI is required for RulesAdapter source compression.',
	)
	_require_binary(
		tool='git',
		candidates=('git',),
		install_instructions='Install Git via your system package manager or https://git-scm.com/downloads',
		reason='Git is required for staleness detection and repository history analysis.',
	)
	_require_provider_cli()
	_ensure_codebase_memory_mcp()


def _require_python_module(module_name: str, install_instructions: str, reason: str) -> None:
	if importlib.util.find_spec(module_name) is not None:
		return
	raise PrerequisiteError(module_name, reason, install_instructions)


def _require_binary(
	tool: str, candidates: tuple[str, ...], install_instructions: str, reason: str
) -> str:
	for candidate in candidates:
		location = which(candidate)
		if location is not None:
			return location
	raise PrerequisiteError(tool, reason, install_instructions)


def _require_provider_cli() -> None:
	if which('claude') is not None or which('codex') is not None:
		return
	raise PrerequisiteError(
		'provider CLI',
		'Neither the claude nor codex CLI was found in PATH.',
		'Install Claude Code or Codex CLI and ensure the binary is available in PATH',
	)


def _ensure_codebase_memory_mcp() -> Path:
	existing = _find_codebase_memory_mcp()
	if existing is not None:
		return existing
	return _download_codebase_memory_mcp()


def _find_codebase_memory_mcp() -> Path | None:
	installed_path = _local_codebase_memory_mcp_path()
	if installed_path.exists() and os.access(installed_path, os.X_OK):
		return installed_path

	path_location = which(CODEBASE_MEMORY_MCP)
	if path_location is None:
		return None
	return Path(path_location)


def _download_codebase_memory_mcp() -> Path:
	download_url = _codebase_memory_mcp_download_url()
	target_path = _local_codebase_memory_mcp_path()
	target_path.parent.mkdir(parents=True, exist_ok=True)

	try:
		with urlopen(download_url, timeout=30) as response:  # nosec B310
			archive_bytes = response.read()
	except OSError as error:
		raise PrerequisiteError(
			CODEBASE_MEMORY_MCP,
			'The auto-download failed while fetching the release archive.',
			(
				f'Download the correct archive from {download_url} and place the '
				f'{CODEBASE_MEMORY_MCP} binary in {target_path.parent}'
			),
		) from error

	try:
		binary_bytes = _extract_codebase_memory_mcp_binary(archive_bytes)
	except (tarfile.TarError, ValueError) as error:
		raise PrerequisiteError(
			CODEBASE_MEMORY_MCP,
			'The downloaded archive could not be unpacked safely.',
			(
				f'Download the correct archive from {download_url} and place the '
				f'{CODEBASE_MEMORY_MCP} binary in {target_path.parent}'
			),
		) from error

	target_path.write_bytes(binary_bytes)
	target_path.chmod(_executable_mode(target_path))
	return target_path


def _extract_codebase_memory_mcp_binary(archive_bytes: bytes) -> bytes:
	with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode='r:gz') as archive:
		for member in archive.getmembers():
			if not member.isfile():
				continue
			if Path(member.name).name != CODEBASE_MEMORY_MCP:
				continue
			extracted = archive.extractfile(member)
			if extracted is None:
				break
			return extracted.read()
	raise ValueError('Archive did not contain the expected binary')


def _codebase_memory_mcp_download_url() -> str:
	system = platform.system()
	machine = platform.machine()
	try:
		return CODEBASE_MEMORY_MCP_RELEASES[(system, machine)]
	except KeyError as error:
		raise PrerequisiteError(
			CODEBASE_MEMORY_MCP,
			f'No supported auto-download is configured for platform {system}/{machine}.',
			'Download a matching release manually and place it in ~/.compass/bin',
		) from error


def _local_codebase_memory_mcp_path() -> Path:
	return Path.home() / '.compass' / 'bin' / CODEBASE_MEMORY_MCP


def _executable_mode(path: Path) -> int:
	current_mode = 0
	try:
		current_mode = path.stat().st_mode
	except FileNotFoundError:
		current_mode = 0
	return current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
