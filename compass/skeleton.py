from pathlib import Path

from compass.errors import SkeletonError


def render_skeletons(paths: list[str]) -> dict[str, str]:
	result = {}
	for path in paths:
		if not _is_supported_path(path):
			continue
		try:
			code = Path(path).read_text(encoding='utf-8')
		except (OSError, UnicodeDecodeError) as e:
			raise SkeletonError(str(e)) from e
		try:
			skeleton = _render_grep_ast_skeleton(path, code)
		except Exception:
			skeleton = _render_fallback_skeleton(code)
		if skeleton:
			result[path] = skeleton
	if not result:
		raise SkeletonError('no supported files found')
	return result


def _is_supported_path(path: str) -> bool:
	try:
		from grep_ast.parsers import filename_to_lang

		return bool(filename_to_lang(path))
	except Exception:
		return Path(path).suffix in {'.py', '.ts', '.tsx', '.js', '.jsx'}


def _render_grep_ast_skeleton(path: str, code: str) -> str:
	from grep_ast.grep_ast import TreeContext

	tc = TreeContext(path, code, child_context=False)
	tc.show_lines = {
		i for i, nodes in enumerate(tc.nodes) if any(n.end_point[0] > i for n in nodes)
	}
	return tc.format()


def _render_fallback_skeleton(code: str) -> str:
	lines: list[str] = []
	for line in code.splitlines():
		stripped = line.strip()
		if not stripped:
			continue
		if line.startswith(('class ', 'def ', 'async def ')):
			lines.append(line)
			continue
		if line.startswith((' ', '\t')):
			continue
		lines.append(line)
	return '\n'.join(lines)
