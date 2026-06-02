# Contributing to Compass

Compass is a CLI tool that scans a codebase and generates structured onboarding artifacts. This guide covers everything you need to work autonomously — from setup to merging a PR.

---

## Communication — Discord

We use Discord as our primary async communication channel.

| Channel | Purpose |
|---|---|
| `#general` | Team announcements, check-ins |
| `#dev` | Technical discussions, architecture questions, blockers |
| `#pr-reviews` | Post your PR link here when it's ready for review |
| `#releases` | Merge announcements, milestone completions |
| `#random` | Off-topic |

**Norms:**
- Async-first — don't expect instant replies. 24–48h turnaround is the default.
- Before opening a new thread in `#dev`, check if a related discussion exists.
- If your task touches another contributor's area, ping them directly in `#dev` — don't assume they'll see your PR.
- Sam reviews PRs **1–2x per week**. Post in `#pr-reviews` when your PR is ready, don't wait for him to find it.

---

## Getting Started

**Prerequisites:**
- Python 3.11+
- [`ast-grep`](https://ast-grep.github.io/) (for integration tests)
- [`repomix`](https://github.com/yamadashy/repomix) (for integration tests)

**Setup:**
```bash
git clone https://github.com/Sammyduzit/compass.git
cd compass
pip install -e ".[dev]"
```

**Run tests:**
```bash
pytest                        # unit tests only (fast, no external binaries)
pytest --run-integration      # unit + integration tests
pytest -m integration         # integration tests only
```

**Run code quality checks:**
```bash
ruff check compass/           # linting
mypy compass/                 # type checking
bandit -r compass/            # security scan
```

See [TESTING.md](TESTING.md) for the full testing strategy and mock boundaries.

---

## How We Work

**Task scope:** Each task covers a complete feature — implementation, tests, code quality, and verification that everything runs. You own it end-to-end.

**Autonomy:** You are expected to make reasonable implementation decisions without waiting for approval. When something is genuinely unclear (architecture-level decisions, cross-module boundaries), ask in `#dev` rather than stalling.

**Coordination:** If your task depends on another contributor's work, or modifies shared interfaces, reach out in `#dev` early — before implementation, not after. Check the issue description for "Related Issues" and ping the relevant people.

**Reference docs:**
- [FINAL.md](FINAL.md) — canonical architecture decisions (locked)
- [STRUCTURE.md](STRUCTURE.md) — where code belongs
- [TESTING.md](TESTING.md) — testing philosophy and mock boundaries

---

## Branch Strategy

```
feature/<short-name>  →  dev  →  main
```

- Branch off `dev`, not `main`.
- Name your branch `feature/<short-name>` (e.g. `feature/fastapi-layer`, `feature/summary-adapter`).
- `dev → main` merges happen at milestone checkpoints, reviewed by Sam.

---

## Commit Messages

- Short, imperative, English (e.g. `add summary adapter`, `fix file selector churn score`)
- No verbose descriptions in the commit message — that belongs in the PR body.
- No co-author credits or AI mentions.

---

## PR Process

### 1. Open a Draft PR early

As soon as you have a rough direction, open a Draft PR and link it in `#dev`. This allows for early directional feedback before significant work is invested.

### 2. Link the issue

Every PR must close an issue:
```
Closes #42
```

### 3. Self-assign the issue

Assign yourself to the GitHub issue when you start working on it. Add the `WIP` label while in progress.

### 4. Before marking Ready for Review

- All Definition of Done items are checked (see below)
- CI is passing
- Switch PR from Draft → Ready for Review
- Add the `ready for review` label
- Post the PR link in `#pr-reviews`

### 5. Review

Sam reviews PRs 1–2x per week. Expect feedback within a few days. Address review comments and re-request review when done.

---

## Definition of Done

Before marking a PR as "Ready for Review", verify every item:

- [ ] Implementation complete and working
- [ ] Unit tests written for new logic
- [ ] Integration tests written where applicable (see [TESTING.md](TESTING.md))
- [ ] `ruff check compass/` — clean
- [ ] `mypy compass/` — clean
- [ ] `bandit -r compass/` — clean
- [ ] CI passing (all jobs green)
- [ ] Docs updated if the change affects architecture, structure, or public behavior (FINAL.md, STRUCTURE.md, etc.)

---

## Code Quality

We enforce three tools automatically in CI:

| Tool | Purpose | Config |
|---|---|---|
| `ruff` | Linting + formatting | `pyproject.toml` |
| `mypy` | Static type checking | `pyproject.toml` |
| `bandit` | Security scanning | CI config |

Run all three locally before pushing. CI will catch failures, but fixing locally is faster.

---

## Milestones

Features are grouped into GitHub Milestones. Before starting work, check which milestone your issue belongs to — this gives context on priority and sequencing.

Current milestones are tracked at: https://github.com/Sammyduzit/compass/milestones

---

## Coding Conventions

A few project-specific rules that override common defaults:

- **No `models.py`** — each data model gets its own file (e.g. `analysis_context.py`, `file_score.py`).
- **`runner.py` stays separate from `cli.py`** — pipeline logic in `runner.py`, `cli.py` is a thin wrapper only.
- **No `logging.py`** — use `log.py` to avoid shadowing the stdlib.
- **Comments only for non-obvious WHY** — don't explain what the code does, only why it does something surprising.
- **Async-first** — all collectors are async, `cli.py` uses `asyncio.run()` as the single event loop entry point.
