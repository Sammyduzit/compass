# Compass — Final Decisions

> Single source of truth for all implementation decisions.  
> When in doubt during implementation: this file wins.  
> Detailed rationale → docs/archive/COLLECTORS_RATIONALE.md (collector stack, archived), FRONTEND.md (frontend path).

---

## Name & Language
**Compass** — final. **Python** — v1 CLI is Python.

## Architecture: Port-Adapter
```
Collectors (no LLM) → AnalysisContext (persisted JSON) → Adapters (one LLM call each)
```
- Phase 1: pure data gathering, zero LLM cost, runs once and persists
- Phase 2: one focused LLM call per adapter, independent, re-runnable without re-collecting

## Entry Point: runner.py separation from day one
```
cli.py    ← thin wrapper: parses args, calls Runner
runner.py ← all pipeline logic, no CLI knowledge
api/      ← FastAPI (v2): calls the same Runner
```
This separation is non-negotiable from commit one. It is what enables the v2 frontend without a refactor.

## Frontend: v2
Next.js + FastAPI on top of runner.py. See FRONTEND.md for full architecture.  
Parallel frontend dev is possible as soon as the API contract is defined — frontend team mocks the API, backend team builds runner.py independently.

## LLM Providers: both claude AND codex in v1
Both providers must be functional in v1. The team uses both.
- Prerequisites check: at least one provider required; hard error if both missing
- Default: configurable in .compass/config.yaml
- No max_budget_usd default — the flag targets agentic runs, not single-shot non-interactive mode

## Structured Output / Schema Enforcement
Outputs are YAML (`rules.yaml`) and Markdown (`summary.md`) — no JSON involved.
- Schema is embedded in each adapter's prompt template ("Output YAML matching this schema: ...")
- After each LLM call: parse output + validate against schema → 1 retry on failure → hard error
- No CLI flags for schema enforcement — prompt + validation is the full solution

## Collector Stack (v1)
Full rationale in `docs/archive/COLLECTORS_RATIONALE.md`.

| Collector | Role | Phase |
|-----------|------|-------|
| **codebase-memory-mcp** via official MCP Python SDK | centrality scores + Louvain call-graph clusters | 1 |
| **ast-grep** | pattern extraction (error handling, decorators, naming) — output consumed by RulesAdapter only | 1 |
| **git log parser** | churn score + logical coupling pairs + code age — one pass, ~100 lines Python | 1 |
| **docs_reader** | CONTRIBUTING.md, ADRs, .cursor/rules, README (root only) — output consumed by RulesAdapter only | 1 |
| **grep_ast** | skeleton rendering per adapter (signatures, class shapes, no bodies) | 2 |
| **repomix** | `--compress` on FileSelector files — implementation bodies for RulesAdapter | 2 |
| **FileSelector** | per-adapter file selection with apply_coverage() post-pass | 2 |

All Phase 1 collectors always run to produce a complete AnalysisContext. "Consumed by RulesAdapter only" means the output section is not included in SummaryAdapter's `build_prompt()` — not that the collector is skipped.

Not in v1: **git_semantics** (v2). repomix is in v1 for RulesAdapter bodies (not as a generic blob source).

## Import Graph: codebase-memory-mcp via official MCP Python SDK
- Static binary, zero system dependencies — no Node.js required
- Louvain community detection on **call graph** (richer than import graph — captures runtime dependencies, not just static imports)
- Centrality + call-graph clustering closes domain-coverage gaps that behavioral signals alone cannot address
- Official MCP Python SDK (`pip install mcp`, installed with Compass) replaces mcp2py — Anthropic-maintained, full timeout/error control
- Wrapped in `ImportGraphCollector` — **Async decision: Runner is fully `async`. All collectors are awaitable. cli.py uses a single `asyncio.run(runner.run(...))` at the entry point. This is the only collector with a live subprocess + async protocol, and the reason the async-first design was chosen (v2 FastAPI compatibility included).**

## FileSelector
- Per-adapter file selection — not uniform context for all adapters
- `apply_coverage()` post-pass guarantees category representation — categories are per-language (python / typescript / generic each have their own set)

## Language Auto-Detection: v1
Python + TypeScript/JS auto-detected from file distribution. Generic fallback for other languages.
```
prompts/
  extract_rules.md          ← generic fallback
  extract_rules_python.md
  extract_rules_ts.md
  summary.md
  summary_python.md
  summary_ts.md
```
Override: `--lang python|typescript`

## v1 Adapters

**RulesAdapter → rules.yaml**
- FileSelector: low-churn + high-centrality + high-coupling-pairs + apply_coverage()
- Context: grep_ast skeletons (structural overview) + repomix --compress bodies (unanticipated pattern discovery) + ast-grep patterns + git signals + docs_reader + centrality/clustering
- The hybrid is intentional: grep_ast shows shape, repomix bodies let the LLM discover project-specific idioms it wasn't queried for
- Output schema: two-level cluster → rules (id, rule, why, example) — see examples/rules.yaml

**SummaryAdapter → summary.md**
- FileSelector: high-centrality + hotspots
- Context: grep_ast skeletons only (structure is enough, no implementation bodies needed)
- No repomix, no ast-grep patterns, no docs_reader
- **Why no ast-grep patterns:** ast-grep answers "how is code written" (conventions, error handling style) — that is RulesAdapter's domain. SummaryAdapter answers "what does this do and how is it structured." grep_ast skeletons + git signals are sufficient; adding ast-grep patterns would pull the LLM toward convention output instead of architectural summary.

## AnalysisContext — v1 sections
```json
{
  "architecture": {
    "file_scores": [{ "path": "...", "churn": 0.0, "age": 0, "centrality": 0.0, "cluster_id": 0, "coupling_pairs": [] }],
    "coupling_pairs": [],
    "clusters": [{ "id": 0, "files": ["..."] }]
  },
  "patterns":     { "error_handling": "...", "naming": "..." },
  "git_patterns": { "hotspots": [...], "stable_files": [...], "coupling_clusters": [...] },
  "docs":         { "CONTRIBUTING.md": "...", "docs/adr/001.md": "..." }
}
```
- Persisted to `.compass/analysis_context.json`; staleness detection via `git rev-parse HEAD`
- grep_ast skeletons NOT stored — each adapter calls FileSelector + grep_ast at Phase 2 runtime
- `--reanalyze` forces fresh Phase 1

## Output
```
target-repo/
└── .compass/
    ├── analysis_context.json     ← Phase 1 output (persisted)
    ├── repo_state.json           ← staleness fingerprint (git rev-parse HEAD)
    └── output/
        ├── rules.yaml
        └── summary.md
```

## CLI
```bash
compass /path/to/repo --adapters rules
compass /path/to/repo --adapters rules,summary
compass /path/to/repo --adapters all
compass /path/to/repo --adapters rules --provider claude|codex
compass /path/to/repo --adapters rules --lang python|typescript
compass /path/to/repo --adapters rules --reanalyze
```

## Configuration
```yaml
# .compass/config.yaml  (project-level)
# ~/.compass/config.yaml (global)
default_provider: claude   # or: codex
lang: auto                 # auto | python | typescript
```

## Prerequisites (v1)
```
1. grep_ast            pip — installed with Compass
2. mcp (MCP Python SDK) pip — installed with Compass
3. ast-grep            brew/cargo — hard error with install instructions if missing
4. repomix             brew/npm — hard error with install instructions if missing
5. git                 always present
6. claude OR codex     hard error + install instructions if both missing
7. codebase-memory-mcp static binary — auto-install via Python urllib (platform detection → ~/.compass/bin/); hard error if download fails; auto-index on first run per repo
```

## Distribution
```bash
git clone https://github.com/Sammyduzit/compass
cd compass
pip install -e .
compass /path/to/target-repo --adapters rules,summary
```
No package registry. Internal tool.

## rules.yaml schema
Two-level: Cluster (context + golden_file) → Rules (id, rule, why, example). Schema locked — see examples/rules.yaml.

## Non-Goals (v1)
- Does not write or scaffold code
- Not interactive — runs through, produces files, exits
- Not a linter, formatter, or PR review tool
- Not a documentation replacement — fills gaps

---

## v2 Scope

| Feature | Note |
|---------|------|
| Frontend: Next.js + FastAPI | runner.py separation in v1 is the prerequisite |
| DocsAdapter → ARCHITECTURE.md, ADRs | repomix required as v2 dependency |
| SkillAdapter → Claude Code Skills | input: AnalysisContext + optional rules.yaml |
| git_semantics collector | pattern-based default; LLM analysis via feature flag |
| Anthropic API direct provider | opt-in, config-driven |
| Language templates: Go, Java, others | extend prompts/ |
