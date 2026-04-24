from pathlib import Path

from grep_ast.grep_ast import TreeContext
from grep_ast.parsers import filename_to_lang

from compass.errors import SkeletonError


def render_skeletons(paths: list[str]) -> dict[str, str]:
	result = {}
	for path in paths:
		if not filename_to_lang(path):
			continue
		try:
			code = Path(path).read_text(encoding='utf-8')
		except (OSError, UnicodeDecodeError) as e:
			raise SkeletonError(str(e)) from e
		tc = TreeContext(path, code, child_context=False)
		tc.show_lines = {
		    i for i, nodes in enumerate(tc.nodes)
			if any(n.end_point[0] > i for n in nodes)
		}
		skeleton = tc.format()
		if skeleton:
			result[path] = skeleton
	if not result:
		raise SkeletonError('no supported files found')
	return result
