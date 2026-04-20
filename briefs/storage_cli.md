# Brief: Storage & CLI

Your job is to write the **pipeline skeleton** — the entry point, the runner, the file selector, prerequisites checking, language detection, and all persistence. This is the glue that connects Phase 1 (collectors) and Phase 2 (adapters).

**Prerequisite:** The foundation files (`errors.py`, `config.py`, `paths.py`) must be finished before you start.

Note: `analysis_context_store.py` and `file_selector.py` depend on the domain models (`compass/domain/`), which another team is writing in parallel. Write those two files last, or stub the imports and fill them in once the domain models are available.

---

## What you're building

```
compass/cli.py
compass/runner.py
compass/prerequisites.py
compass/language_detection.py
compass/file_selector.py
compass/storage/
├── __init__.py
├── analysis_context_store.py
├── output_writer.py
├── repo_state_hash.py
└── repo_state_store.py
```

---

## Reference files — read these first

- **`FINAL.md`** → sections "CLI", "Configuration", "Prerequisites", "Output", "AnalysisContext"
- **`STRUCTURE.md`** → sections for each file listed above (read all of them)
- **`TESTING.md`** → section "Unit Test Scope" — `test_cli.py`, `test_runner.py`, `test_file_selector.py`, `test_prerequisites.py`

---

## Part 1 — cli.py

This file must stay thin. All pipeline logic goes in `runner.py`. `cli.py` only parses args and calls the Runner.

- How do you parse the CLI arguments listed in FINAL.md? (`--adapters`, `--provider`, `--lang`, `--reanalyze`)
- How do you expand `--adapters all` into the full list?
- How do you load the config files (project-level + global) and merge with CLI args? (CLI args win)
- How do you construct a `CompassConfig` and pass it to `runner.run()`?
- The runner is async — how does `cli.py` handle that? (hint: one `asyncio.run()` call, nothing else)
- What does the user see if they pass an invalid argument?

---

## Part 2 — runner.py

The pipeline orchestrator. No CLI knowledge here — it only knows about `CompassConfig`.

- What is the exact sequence of steps? (See STRUCTURE.md → `compass/runner.py` for the full flow diagram)
- How does it decide whether to run Phase 1 or skip it? (staleness check — what does "stale" mean?)
- How does it hand off to the `CollectorOrchestrator` for Phase 1?
- How does it hand off to the `AdapterOrchestrator` for Phase 2?
- What happens when a `CollectorError` or `AdapterError` is raised — does it catch it or let it propagate?
- Why must this file have zero knowledge of `argparse` or `sys.argv`?

---

## Part 3 — prerequisites.py

Called first in `runner.run()`. Checks that all required tools are installed.

- What are the 7 prerequisites? (See FINAL.md → "Prerequisites")
- How do you check if a binary exists on the system?
- For `codebase-memory-mcp`: it needs to be auto-downloaded if missing. How do you do that with `urllib`? Where does it go? (`~/.compass/bin/`)
- The rule for providers: at least one of `claude` OR `codex` must be present. Both missing = hard error.
- Every failure must raise `PrerequisiteError` with a message that includes install instructions. What do those messages look like for each tool?

---

## Part 4 — language_detection.py

Detects the primary language of the target repo.

- How do you determine the language from file distribution? (count `.py` vs `.ts`/`.js` files)
- What thresholds make sense for returning `"python"` vs `"typescript"` vs `"generic"`?
- The result is used in two places: prompt template selection and `FileSelector` category sets. Does that affect your interface?
- How does `CompassConfig.lang` override auto-detection?

---

## Part 5 — file_selector.py

The join between Phase 1 signals and Phase 2 adapter input. Selects the most relevant files per adapter.

- What signals from `AnalysisContext` does it consume? (centrality, churn, coupling pairs)
- How do you score and rank files differently for RulesAdapter vs SummaryAdapter? (See FINAL.md → "FileSelector")
- What is `apply_coverage()`? What problem does it solve? How do language-specific category sets work?
- This is never called directly by adapters — it's called via `adapters/base.run_file_selector()`. Does that change your interface design?
- What should it return — a list of file paths?

---

## Part 6 — storage/

Four focused files. Each has one job.

**`repo_state_hash.py`**
- How do you compute the repo fingerprint? (hint: `git rev-parse HEAD`)
- What does it return?

**`repo_state_store.py`**
- Reads and writes `repo_state.json` in the target repo's `.compass/` directory
- How do you check if the current HEAD matches the stored fingerprint?

**`analysis_context_store.py`**
- Reads and writes `analysis_context.json`
- How do you serialize/deserialize the `AnalysisContext` dataclass to/from JSON?

**`output_writer.py`**
- Writes adapter outputs (`rules.yaml`, `summary.md`) to `.compass/output/`
- How do you ensure the output directory exists before writing?

---

## Testing

Write the following unit test files in `tests/unit/`. Read TESTING.md → "Unit Test Scope" for the full list of cases each file must cover.

| Test file | What it covers |
|---|---|
| `test_cli.py` | Arg parsing, `--adapters all` expansion, config precedence, correct `CompassConfig` constructed |
| `test_runner.py` | Phase 1 skipped when cache fresh, runs when stale or `--reanalyze`, error propagation |
| `test_prerequisites.py` | `PrerequisiteError` for each missing binary, provider logic |
| `test_language_detection.py` | Language heuristic per fixture profile, `--lang` override |
| `test_file_selector.py` | Selection criteria, `apply_coverage()`, language-specific category sets |

Mock all external calls (git subprocess, filesystem where practical via `tmp_path`).

---

## Definition of done

- [ ] `compass /path/to/repo --adapters rules` runs end-to-end without crashing (even with mocked collectors/adapters)
- [ ] `cli.py` contains zero pipeline logic — only arg parsing + `asyncio.run()`
- [ ] `runner.py` contains zero CLI knowledge — only `CompassConfig` as input
- [ ] Phase 1 is skipped when `analysis_context.json` exists and HEAD hasn't changed
- [ ] `--reanalyze` forces Phase 1 regardless of staleness
- [ ] All prerequisite failures raise `PrerequisiteError` with install instructions
- [ ] All storage operations go through `compass/storage/` — nothing else writes to `.compass/`
- [ ] All 5 unit test files written with cases from TESTING.md
