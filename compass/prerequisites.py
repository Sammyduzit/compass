from __future__ import annotations

import shutil

from compass.errors import PrerequisiteError


def check() -> None:
	if not shutil.which('repomix'):
		raise PrerequisiteError(
			'repomix',
			'Required for RulesAdapter body collection.',
			'brew install repomix  OR  npm install -g repomix',
		)
