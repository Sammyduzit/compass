from __future__ import annotations

import re

from compass.errors import TemplateNotFoundError
from compass.paths import templates_dir

_TEMPLATES_DIR = templates_dir()

_TEMPLATE_FILES: dict[str, str] = {
	'extract_rules': 'extract_rules.md',
	'reconciliation': 'reconciliation.md',
	'summary': 'summary.md',
}

_LANGUAGE_BLOCK = re.compile(
	r'<!-- LANGUAGE:(\w+) -->(.*?)<!-- /LANGUAGE:\1 -->',
	re.DOTALL,
)


def load_template(template: str, lang: str) -> str:
	"""
	template: "extract_rules" | "reconciliation" | "summary"
	lang:     "python" | "typescript" | "generic"
	returns:  full prompt string ready to send to LLM
	"""
	if template not in _TEMPLATE_FILES:
		raise TemplateNotFoundError(template, sorted(_TEMPLATE_FILES))

	content = (_TEMPLATES_DIR / _TEMPLATE_FILES[template]).read_text(encoding='utf-8')

	# Strip the leading metadata comment (for editors, not for the LLM).
	# The closing --> sits on its own line; match to \n--> so we don't stop
	# early at any inline <!-- ... --> references inside the comment block.
	content = re.sub(r'^\s*<!--.*?\n-->\s*', '', content, count=1, flags=re.DOTALL)

	matches = {m.group(1): m.group(2).strip() for m in _LANGUAGE_BLOCK.finditer(content)}

	if not matches:
		return content.strip()

	first = _LANGUAGE_BLOCK.search(content)
	if first is None:
		raise RuntimeError('unreachable: LANGUAGE blocks detected but search returned None')
	shared = content[: first.start()].strip()

	lang_content = matches.get(lang) or matches.get('generic', '')

	return f'{shared}\n\n{lang_content}'.strip()
