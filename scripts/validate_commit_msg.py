"""Validate Compass commit messages for the pre-commit commit-msg hook."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PATTERN = re.compile(
	r'^(feat|fix|docs|style|refactor|test|chore|ci|build|perf|revert)'
	r'(\([a-z0-9._-]+\))?: .{1,72}$'
)


def main(argv: list[str] | None = None) -> int:
	args = sys.argv[1:] if argv is None else argv
	if len(args) != 1:
		print('Usage: validate_commit_msg.py <commit-msg-file>', file=sys.stderr)
		return 2

	message = Path(args[0]).read_text(encoding='utf-8').strip()
	first_line = message.splitlines()[0] if message else ''
	if PATTERN.match(first_line):
		return 0

	print(
		'Invalid commit message.\n\n'
		'Use Conventional Commits:\n'
		'  <type>(optional-scope): <short summary>\n\n'
		'Allowed types: feat, fix, docs, style, refactor, test, chore, ci, '
		'build, perf, revert.\n'
		'Examples:\n'
		'  feat(foundation): add config dataclass\n'
		'  test: add fixture setup script',
		file=sys.stderr,
	)
	return 1


if __name__ == '__main__':
	raise SystemExit(main())
