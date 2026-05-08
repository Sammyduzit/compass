# Foundation Update For All Teams

The foundation branch now includes a commit message convention hook via
pre-commit.

Run this once locally after pulling the branch:

```bash
pip install pre-commit
pre-commit install --hook-type commit-msg
```

Commit messages must use Conventional Commits:

```text
<type>(optional-scope): <short summary>
```

Allowed types:

```text
feat, fix, docs, style, refactor, test, chore, ci, build, perf, revert
```

Examples:

```text
feat(foundation): add config dataclass
test: add fixture setup script
```
