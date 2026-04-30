# Compass — Testing Strategy

> When in doubt about where a test belongs or what to mock: this file wins.

---

## Philosophy

Tests verify that the **pipeline orchestration and logic are correct** — not that external tools (ast-grep, repomix, LLM providers, MCP binary) work correctly. External tools are mocked at the boundary. Real binaries are only required for integration tests, and only where the fixture-to-output contract matters.

---

## Test Tiers

| Tier | Location | Runs in CI | External binaries needed |
|---|---|---|---|
| Unit | `tests/unit/` | Always (every push) | None |
| Integration | `tests/integration/` | Separate CI job (PRs + manual) | `ast-grep`, `repomix` |

Mark integration tests with `@pytest.mark.integration`. Run locally with:

```bash
pytest                              # unit only (default)
pytest --run-integration            # unit + integration
pytest -m integration               # integration only
```

---

## Mock Boundaries

### Unit tests — always mock

| What | Why |
|---|---|
| LLM provider (`call_provider()`) | Non-deterministic, costs CLI credits |
| `ast-grep` binary | Testing pattern-extraction logic, not the binary |
| `grep_ast` library calls | Testing skeleton-rendering logic, not the library |
| `repomix` binary | Testing body-collection logic, not the binary |
| `ImportGraphCollector` / MCP binary | Async subprocess path tested in isolation; pipeline tests mock the output |
| Filesystem (where practical) | Use `tmp_path` pytest fixture |
| `git` subprocess calls | Use fixture repos with real history (see below) — mock in unit |

### Integration tests — mock only the LLM

| What | Real or Mock |
|---|---|
| LLM provider | **Mock** — returns controlled, schema-valid output |
| `ast-grep` binary | Real (installed in CI) |
| `grep_ast` library | Real (pip, installed with Compass) |
| `repomix` binary | Real (installed in CI) |
| `ImportGraphCollector` / MCP binary | **Mock** — returns fixture centrality + cluster data |
| `git` | Real — fixture repos have scripted git history |
| Filesystem | Real — fixture repos on disk |

**Why mock the MCP binary in integration?** The async subprocess protocol is covered by unit tests for `ImportGraphCollector`. Integration tests target pipeline orchestration. If the binary is missing, `prerequisites.check()` catches it — that is not a pipeline test case.

**Why mock the LLM provider in integration?** Correctness of LLM output is a prompt-engineering concern, not a code-correctness concern. Integration tests verify that the adapter collects the right data, assembles the prompt correctly, validates output, and writes artifacts. A controlled mock response is sufficient and keeps tests deterministic.

---

## Fixtures

All fixture repos are **synthetic** — hand-crafted with known patterns, scripted git history. No dependency on external open-source code.

### `sample_repo_minimal/`

3–5 files, no language-specific patterns. Used for:
- Smoke tests (happy path, does the full pipeline complete?)
- Error-handling tests (missing file, empty repo, no commits)
- Staleness / `--reanalyze` flow tests

Must have: initialized git repo with at least 2 commits.

### `sample_repo_python/`

15–20 files. Contains deliberate Python patterns that collectors and adapters act on:
- Decorators (`@property`, `@staticmethod`, custom)
- Error handling patterns (try/except in specific locations)
- Import structure with clear high-centrality files
- Multiple commits with known churn distribution (at least one hot file, at least one stable file)
- A `CONTRIBUTING.md` for `DocsReaderCollector`

Used for: `test_run_rules.py`, `test_run_summary.py` with language-specific assertions.

### `sample_repo_typescript/`

Same structure as Python fixture, TypeScript idioms (interfaces, async/await, decorators). Used for the same integration tests with `--lang typescript`.

### Fixture git history

All fixtures are initialized as real git repos with scripted history. The fixture setup script (`tests/fixtures/setup.sh` or equivalent) must be idempotent and committed. CI recreates fixture repos from script, not from a checked-in `.git/` directory.

Build fixtures locally with:

```bash
tests/fixtures/setup.sh sample_repo_minimal
tests/fixtures/setup.sh sample_repo_python
tests/fixtures/setup.sh sample_repo_typescript
tests/fixtures/setup.sh all
```

The script deletes and recreates the selected fixture repo each time, so rerunning it is the supported way to reset fixture history.

---

## Unit Test Scope

| File | What it tests |
|---|---|
| `test_cli.py` | Arg parsing → correct `CompassConfig` fields. `--adapters all` expansion. Config file precedence (CLI > project > global). That `runner.run()` is called with the right config. Error messages for invalid args. |
| `test_runner.py` | Phase 1 skipped when cache is fresh. Phase 1 runs when stale or `--reanalyze`. Phase 2 loops through all requested adapters. `CollectorError` and `AdapterError` propagate correctly. |
| `test_file_selector.py` | Selection criteria produce correct file rankings. `apply_coverage()` adds missing category representatives. Language-specific category sets (python / typescript / generic). |
| `test_language_detection.py` | File distribution heuristic returns correct language for each fixture profile. `--lang` override respected. |
| `test_prerequisites.py` | `PrerequisiteError` raised with install instructions for each missing binary. At least one provider present = no error. Both providers missing = hard error. |
| `test_rules_adapter.py` | `build_prompt()` includes all expected context sections. `validate_output()` passes valid schema. `validate_output()` triggers 1 retry on invalid output. Hard error after second failure. |
| `test_summary_adapter.py` | `build_prompt()` includes grep_ast skeletons + git signals only — no ast-grep patterns, no docs section. Same validation flow as rules adapter. |

---

## Integration Test Scope

| File | What it tests |
|---|---|
| `test_run_rules.py` | Full pipeline on `sample_repo_python` and `sample_repo_typescript`. Asserts that `rules.yaml` is written to `.compass/output/`. Asserts that output passes schema validation. Spot-checks that at least one cluster was identified. |
| `test_run_summary.py` | Full pipeline on same fixtures for SummaryAdapter. Asserts that `summary.md` is written. Asserts that output is non-empty Markdown. |
| `test_reanalyze_flow.py` | Run pipeline twice on `sample_repo_minimal`. Second run skips Phase 1 (assert collectors not called again). Modify git HEAD (add a commit). Third run re-runs Phase 1. `--reanalyze` forces Phase 1 regardless of staleness. |

---

## CI Setup

### Unit job (every push)
```yaml
- run: pip install -e ".[dev]"
- run: pytest tests/unit/
```

### Integration job (PRs + manual trigger)
```yaml
- run: brew install ast-grep
- run: brew install repomix      # or npm install -g repomix
- run: pip install -e ".[dev]"
- run: tests/fixtures/setup.sh all
- run: pytest --run-integration tests/integration/
```

The integration job does **not** install `codebase-memory-mcp` — `ImportGraphCollector` is mocked at the boundary.

---

## What Is Not Tested Here

- LLM output quality — that is prompt engineering, verified manually against real repos
- `codebase-memory-mcp` binary behavior — tested by running Compass end-to-end against a real repo manually
- Provider CLI behavior (claude / codex subprocess) — assumed correct; only the subprocess interface is mocked in tests
