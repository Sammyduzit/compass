# Compass — Decisions Already Made

> These are locked. They are not up for discussion in brainstorming sessions. When the team works on implementation, these are the constraints they build within.

---

## Name
**Compass** — final.

## Language
**Python** — the v1 CLI is Python. Not Node, not Go, not a shell script.

## Architecture: Port-Adapter
Two distinct phases, no mixing:

```
Collectors (no LLM) → AnalysisContext (persisted JSON) → Adapters (one LLM call each)
```

- **Phase 1 (Collectors):** Pure data gathering. Zero LLM cost. Always runs first.
- **Phase 2 (Adapters):** One focused LLM call per adapter. Independent. Can re-run without re-collecting.

## LLM Integration: CLI subprocess — no direct API
```python
subprocess.run(["claude", "--print", "--output-format", "json", prompt])
```
- No Anthropic API key required — only a CLI subscription
- Structured output enforced via `--json-schema` flag
- Optional budget cap: `--max-budget-usd 0.50`

## Multi-provider design
~10 lines per provider. Adding a new provider = implement one function. v1 ships with `claude` only; `codex` is v2.

## v1 Adapters (scope is fixed)
1. **RulesAdapter** → `rules.yaml` (coding conventions, architectural patterns)
2. **SummaryAdapter** → `summary.md` (onboarding overview for a new developer)

## Output location
All output goes into `.compass/` inside the target repo (add to `.gitignore`):
```
target-repo/
└── .compass/
    ├── analysis_context.json
    └── output/
        ├── rules.yaml
        └── summary.md
```

## CLI interface
```bash
compass /path/to/repo --adapters rules
compass /path/to/repo --adapters rules,summary
compass /path/to/repo --adapters all
compass /path/to/repo --adapters rules --reanalyze
```

## AnalysisContext
- Persisted to disk after Phase 1
- Staleness check: hash of repo state stored alongside context
- If hash differs on next run: warn user, offer `--reanalyze`

## Context slicing
Each adapter declares which sections of AnalysisContext it needs. Only those sections are passed to the LLM. SummaryAdapter does not need `source` — saves ~4k tokens per call automatically.

## rules.yaml schema
Two-level: Cluster (context + golden_file) → Rules (id, rule, why, example). Schema is locked — see `examples/rules.yaml`.

## Distribution
```bash
git clone <repo>
cd compass
pip install -e .
compass /path/to/target-repo --adapters rules
```
No package registry. Internal tool.

## Non-goals (explicit)
- Does not write or scaffold code
- Not interactive — runs through, produces files, exits
- Not a linter, formatter, or PR review tool
- Not a documentation replacement — it fills gaps

---

## Future adapters (planned, not v1 scope)
- **DocsAdapter** → `ARCHITECTURE.md`, ADRs
- **SkillAdapter** → Claude Code Skills (input: AnalysisContext + optional rules.yaml)
- **Language-specific prompts** — auto-detected, per-language prompt templates
