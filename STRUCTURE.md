# Compass — Project Structure

> Implementation reference for all contributors.
> When in doubt about where code belongs: this file wins.
> Architecture decisions → FINAL.md

---

## Repository Layout

```text
compass/                          ← git repo root
├── pyproject.toml
├── README.md
├── .gitignore
├── FINAL.md                      ← single source of truth
├── STRUCTURE.md                  ← this file
├── FRONTEND.md
├── CLAUDE.md
├── examples/
│   ├── rules.yaml
│   ├── summary.md
│   └── analysis_context.json
├── tests/
│   ├── unit/
│   │   ├── test_cli.py
│   │   ├── test_runner.py
│   │   ├── test_file_selector.py
│   │   ├── test_language_detection.py
│   │   ├── test_prerequisites.py
│   │   ├── test_rules_adapter.py
│   │   └── test_summary_adapter.py
│   ├── integration/
│   │   ├── test_run_rules.py
│   │   ├── test_run_summary.py
│   │   └── test_reanalyze_flow.py
│   └── fixtures/
│       ├── sample_repo_minimal/
│       ├── sample_repo_python/
│       └── sample_repo_typescript/
├── docs/
│   └── archive/                  ← superseded documents, do not edit
├── frontend/                     ← Next.js app (v2)
│   ├── package.json
│   └── src/
└── compass/                      ← Python package (everything that gets pip-installed)
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── runner.py
    ├── config.py
    ├── paths.py
    ├── log.py
    ├── errors.py
    ├── language_detection.py
    ├── prerequisites.py
    ├── api/                      ← FastAPI app (v2) — calls runner.py
    │   ├── __init__.py
    │   ├── app.py
    │   └── routes/
    ├── domain/
    │   ├── __init__.py
    │   ├── analysis_context.py
    │   ├── file_score.py
    │   ├── adapter_output.py
    │   ├── architecture_snapshot.py
    │   ├── git_patterns_snapshot.py
    │   ├── coupling_pair.py
    │   └── cluster.py
    ├── collectors/
    │   ├── __init__.py
    │   ├── base.py               ← async base class: all collectors are awaitable
    │   ├── import_graph.py       ← codebase-memory-mcp via MCP Python SDK (async)
    │   ├── ast_grep.py
    │   ├── git_log.py
    │   ├── docs_reader.py
    │   └── orchestrator.py
    ├── file_selector.py          ← per-adapter file selection + apply_coverage()
    ├── adapters/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── rules.py
    │   ├── summary.py
    │   └── orchestrator.py
    ├── providers/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── claude.py
    │   └── codex.py
    ├── prompts/
    │   ├── __init__.py
    │   ├── loader.py
    │   └── templates/
    │       ├── extract_rules.md
    │       ├── reconciliation.md
    │       └── summary.md
    ├── schemas/
    │   ├── __init__.py
    │   ├── rules_schema.py
    │   └── summary_schema.py
    ├── storage/
    │   ├── __init__.py
    │   ├── analysis_context_store.py
    │   ├── output_writer.py
    │   ├── repo_state_hash.py
    │   └── repo_state_store.py
    └── utils/
        ├── __init__.py
        ├── filesystem.py
        ├── json_io.py
        └── subprocess.py
```

---

## Core Principles

- One file per domain model — no `models.py`, no generic containers.
- `runner.py` is separated from `cli.py` from day one — non-negotiable (see FINAL.md).
- All collectors are `async` — the Runner is fully async, `cli.py` calls `asyncio.run(runner.run(...))`.
- Package-local modules must not shadow stdlib — use `log.py`, not `logging.py`.
- Runtime artifacts belong in the target repo's `.compass/` — never inside the Compass source tree.

---

## Package Responsibilities

### `compass/cli.py`

Thin entry point. Parses CLI arguments, builds `CompassConfig`, calls `Runner`. Contains no pipeline logic.

```
cli.py → asyncio.run(runner.run(config))
```

### `compass/config.py`

`CompassConfig` dataclass. Populated by `cli.py` from CLI args + config files, then passed unchanged to `runner.run(config)`. The single object that crosses the CLI/runner boundary.

| Field | Type | Source |
|---|---|---|
| `target_path` | `str` | CLI positional arg |
| `adapters` | `list[str]` | `--adapters rules,summary` or `all` |
| `provider` | `str \| None` | `--provider`, falls back to config.yaml `default_provider` |
| `lang` | `str` | `--lang`, falls back to config.yaml `lang`, default `"auto"` |
| `reanalyze` | `bool` | `--reanalyze` flag |

Config file lookup (lower priority than CLI args): `{target_repo}/.compass/config.yaml`, then `~/.compass/config.yaml`.

### `compass/prerequisites.py`

Called first in `runner.run()`. Checks all 7 prerequisites in order and hard-errors with install instructions if any are missing:

1. `grep_ast` (pip — installed with Compass)
2. `mcp` Python SDK (pip — installed with Compass)
3. `ast-grep` binary (brew/cargo)
4. `repomix` (brew/npm)
5. `git` (assumed present)
6. `claude` OR `codex` CLI (hard error if both missing)
7. `codebase-memory-mcp` binary — auto-installs via urllib to `~/.compass/bin/`; hard error if download fails; auto-indexes on first run per repo

### `compass/language_detection.py`

Detects primary language from file distribution in `target_path`. Returns `"python"`, `"typescript"`, or `"generic"`. Used by `prompts/loader.py` (template selection) and `FileSelector` (`apply_coverage()` category set). Overridden by `Config.lang` when set explicitly.

### `compass/errors.py`

All custom exceptions. Every error Compass can raise is defined here — nothing else raises bare `Exception`.

```
CompassError(Exception)          ← base; catch-all for CLI exit code 1 and API error responses
├── ConfigError                  ← invalid config values (unknown provider, bad lang value)
├── PrerequisiteError            ← missing binary/tool; message includes install instructions
├── CollectorError               ← Phase 1 failure (e.g. MCP subprocess crash, git not a repo)
└── AdapterError                 ← Phase 2 failure
    ├── ProviderError            ← LLM subprocess non-zero exit or timeout
    └── SchemaValidationError    ← LLM output invalid after 1 retry
```

`cli.py` catches `CompassError` at the top level and exits with code 1. `api/` (v2) maps subclasses to HTTP codes (`PrerequisiteError` → 422, `ProviderError` → 502, etc.).

### `compass/runner.py`

All pipeline orchestration. No CLI knowledge. Called by both `cli.py` (v1) and `api/` (v2) without modification.

```
runner.run(config)
    → prerequisites.check()
    → language_detection.detect(repo_path)
    → repo_state_store.is_stale(repo_path)
    │
    ├── PHASE 1 (if stale or --reanalyze)
    │     CollectorOrchestrator
    │       ├── ImportGraphCollector.collect()   → centrality + Louvain clusters
    │       ├── AstGrepCollector.collect()       → error handling, naming patterns
    │       ├── GitLogCollector.collect()        → churn, coupling pairs, code age
    │       └── DocsReaderCollector.collect()    → CONTRIBUTING.md, ADRs, etc.
    │     → assemble AnalysisContext
    │     → analysis_context_store.write()
    │
    └── PHASE 2 (per requested adapter)
          AdapterOrchestrator
            └── adapter.run(analysis_context)
                  ├── 1. base.run_file_selector(criteria)   → FileSelector + apply_coverage()
                  ├── 2. base.run_grep_ast(files)           → skeletons for all adapters
                  ├── 3. self.run_repomix(files)            → bodies [RulesAdapter only]
                  ├── 4. self.build_prompt(...)             → adapter-specific assembly
                  ├── 5. base.call_provider(prompt)         → LLM subprocess
                  ├── 6. base.validate_output(raw)          → schema check + 1 retry
                  └── 7. output_writer.write(result)
```

### `compass/domain/`

Core data structures. Independent of CLI, providers, and collectors.

| File | Model |
|---|---|
| `analysis_context.py` | `AnalysisContext` — top-level persisted container |
| `file_score.py` | `FileScore` — churn, age, centrality, cluster_id, coupling_pairs per file |
| `adapter_output.py` | `AdapterOutput` — result envelope for any adapter |
| `architecture_snapshot.py` | Architecture section of AnalysisContext — holds `file_scores`, `coupling_pairs`, `clusters` (Louvain, from ImportGraphCollector) |
| `git_patterns_snapshot.py` | Git signals section of AnalysisContext |
| `coupling_pair.py` | `CouplingPair` — file_a, file_b, degree |
| `cluster.py` | `Cluster` — id + files list; Louvain community unit from ImportGraphCollector |

`domain/` contains only data models — no abstract base classes, no interfaces, no asyncio. Base classes live in their respective packages (`collectors/base.py`, `adapters/base.py`, `providers/base.py`) and are the authoritative contracts for each layer.

### `compass/collectors/`

Phase 1 — pure data gathering, no LLM. All collectors inherit from `base.py` and are `async`.

| File | Collector | Phase |
|---|---|---|
| `import_graph.py` | `ImportGraphCollector` — codebase-memory-mcp via MCP Python SDK. **Async-only: spawns MCP subprocess, communicates via JSON-RPC.** Produces centrality scores + Louvain clusters. | 1 |
| `ast_grep.py` | `AstGrepCollector` — wraps the **`ast-grep`** CLI (brew/cargo). Structural pattern extraction (error handling, decorators, naming). Output stored in AnalysisContext `patterns` section. **Always runs in Phase 1** to produce a complete AnalysisContext — "RulesAdapter only" means the `patterns` section is only consumed by RulesAdapter's `build_prompt()`, not that this collector is skipped for summary-only runs. | 1 |
| `git_log.py` | `GitLogCollector` — churn score, logical coupling pairs, code age. One-pass Python parser. | 1 |
| `docs_reader.py` | `DocsReaderCollector` — CONTRIBUTING.md, ADRs, .cursor/rules, README (root only). **Always runs in Phase 1.** Output consumed by RulesAdapter only — SummaryAdapter does not include the `docs` section in `build_prompt()`. | 1 |
| `base.py` | `BaseCollector` — async abstract base class. All collectors are awaitable. **This is the authoritative contract for collectors — not domain/.** | — |
| `orchestrator.py` | Runs all Phase 1 collectors, assembles and persists `AnalysisContext`. | — |

**Tool naming — two different tools, similar names:**
- **`ast-grep`** (brew/cargo CLI) — used by `AstGrepCollector` in Phase 1. Extracts structural patterns into AnalysisContext.
- **`grep_ast`** (pip Python library, installed with Compass) — used by `adapters/base.run_grep_ast()` in Phase 2. Renders file skeletons for prompt context.

Neither `grep_ast` nor `repomix` are collectors. `utils/subprocess.py` is the raw command runner (executes command, returns stdout). The logic of *when* and *with which files* to invoke them lives in `adapters/base.py` — not duplicated across individual adapters.

### `compass/file_selector.py`

The join between Phase 1 (AnalysisContext signals) and Phase 2 (adapter input).

Consumes `AnalysisContext` signals (centrality, churn, coupling) and selects the minimal relevant file set per adapter. Always applies `apply_coverage()` post-pass to guarantee category representation. **Coverage categories are language-specific** — determined by the `language_detection.detect()` result. Each language has its own category set; `"generic"` uses a minimal fallback.

**Not called directly by adapters.** Invoked via `adapters/base.run_file_selector(criteria)` — this ensures `apply_coverage()` is never accidentally skipped. The selection criteria (which signals to weight, how many files) are passed in by each adapter and differ per adapter.

| Adapter | Criteria |
|---|---|
| RulesAdapter | low-churn + high-centrality + high-coupling-pairs |
| SummaryAdapter | high-centrality + hotspots |

### `compass/adapters/`

Phase 2 — LLM synthesis.

`adapters/base.py` is the shared Phase 2 runtime. It provides:
- `run_file_selector()` — invokes FileSelector with adapter-specific criteria
- `run_grep_ast(files)` — renders skeletons via subprocess
- `call_provider(prompt)` — delegates to the active provider
- `validate_output(raw)` — schema check → 1 retry → hard error

**`build_prompt()` is NOT in base.py** — prompt construction is adapter-specific. Each adapter knows which context sections it needs and how to assemble them. The shared loading mechanism lives in `prompts/loader.py`.

Individual adapters inherit from `base.py` and implement what is unique to them:

| File | Unique logic | Output |
|---|---|---|
| `base.py` | Shared Phase 2 runtime: FileSelector, grep_ast, provider call, validation | — |
| `rules.py` | `build_prompt()` with full context (skeletons + repomix bodies + ast-grep + git + docs), adds `run_repomix()` | `rules.yaml` |
| `summary.py` | `build_prompt()` with grep_ast skeletons + git signals only (no repomix, no ast-grep patterns from AnalysisContext, no docs_reader) | `summary.md` |
| `orchestrator.py` | Loops through `Config.adapters`, instantiates and runs each requested adapter in sequence. | — |

### `compass/providers/`

LLM provider integrations. Hides subprocess details from the rest of the system.

| File | Provider |
|---|---|
| `claude.py` | Claude CLI — v1 |
| `codex.py` | Codex CLI — v1 |
| `base.py` | Shared interface + provider selection logic |

Both providers are v1. No provider registry — a small conditional in `base.py` selects the active provider.

### `compass/prompts/templates/`

Prompt templates are versioned assets, not inline strings. Template selection is language-driven.

| File | Used for |
|---|---|
| `extract_rules.md` | RulesAdapter extraction — language-aware sections within (python / typescript / generic) |
| `reconciliation.md` | RulesAdapter reconciliation pass — language-agnostic |
| `summary.md` | SummaryAdapter — language-aware sections within |

### `compass/schemas/`

Output validation schemas. Each adapter has one. Invalid LLM output fails here → 1 retry → hard error.

### `compass/storage/`

All persistence. Isolated from collectors and adapters.

| File | Responsibility |
|---|---|
| `analysis_context_store.py` | Read/write `analysis_context.json` |
| `output_writer.py` | Write adapter output artifacts |
| `repo_state_hash.py` | Compute repo fingerprint for staleness detection — uses `git rev-parse HEAD` |
| `repo_state_store.py` | Persist repo state metadata |

### `compass/api/` *(v2)*

FastAPI app. Calls `runner.run(config)` — identical to how `cli.py` calls it. No pipeline logic here.

### `frontend/` *(v2)*

Next.js app. Completely separate from the Python package. Own `package.json`, own build process, own dev server.

---

## Runtime Output Location

All generated artifacts go into the **target repository**, never into the Compass source tree.

```text
target-repo/
└── .compass/
    ├── analysis_context.json     ← Phase 1 output (persisted)
    ├── repo_state.json           ← staleness fingerprint
    └── output/
        ├── rules.yaml            ← RulesAdapter output
        └── summary.md            ← SummaryAdapter output
```

---

## Async Architecture

The Runner and all collectors are fully `async`. Entry points handle the event loop boundary:

```
cli.py          → asyncio.run(runner.run(config))
api/app.py (v2) → await runner.run(config)   ← FastAPI is already async
```

`ImportGraphCollector` is the primary reason for this design — it communicates with the codebase-memory-mcp binary via the MCP Python SDK (JSON-RPC over stdio), which is fully `async/await`. Making the entire Runner async avoids nested event loop issues and prepares for v2 FastAPI integration at no extra cost.

---

## Growth Path

| New feature | Goes into |
|---|---|
| New collector | `collectors/` |
| New adapter + output type | `adapters/` + `prompts/templates/` + `schemas/` |
| New LLM provider | `providers/` |
| New language detection heuristic | `language_detection.py` |
| New language prompt variants | `prompts/templates/` |
| New prerequisite check | `prerequisites.py` |
| New persistence concern | `storage/` |

---

## What Not to Add Prematurely

Do not introduce top-level packages for:
- `services/`, `managers/`, `helpers/`, `engine/`, `core/`, `registry/`

Do not add a provider registry until a third provider exists. The conditional in `providers/base.py` is the correct v1 design.

The structure should remain explicit and boring. Prefer specific names and single-purpose files over generic containers.
