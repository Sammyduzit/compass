# VISIONS.md — Compass / CodeAtlas

> **Name:** TBD — shortlist: `Compass`, `CodeAtlas`  
> **Status:** Vision / Pre-Build  
> **Audience:** Internal — team + interns

---

## What is this?

A CLI pipeline tool that scans an unfamiliar codebase and produces structured, actionable artifacts to help a developer get up to speed fast.

**Core use case:** Solo developer joins a project. Instead of spending days reading code, they run one command and get a rules file, a summary, and eventually generated docs — all derived from the actual codebase, not documentation that may be stale.

```bash
compass /path/to/repo --adapters rules,summary
```

---

## Problem it solves

Onboarding to a new codebase is expensive:
- Existing docs are often missing or outdated
- Patterns and conventions live implicitly in the code
- A new dev has no fast path to "what are the rules here?"

Compass extracts what is actually in the code — not what someone hoped would be documented.

---

## Architecture: Port-Adapter

The pipeline has two distinct phases. Phase 1 is pure data collection — no LLM involved, no cost. Phase 2 is synthesis — one focused LLM call per adapter.

```
repo_path
    │
    ▼
┌─────────────────────────────┐
│         COLLECTORS          │  ← no LLM, pure data gathering
│  codebase-memory-mcp        │
│  repomix                    │
│  git analysis               │
└─────────────┬───────────────┘
              │
              ▼
    AnalysisContext (JSON)
    .compass/analysis_context.json  ← persisted to disk
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
┌────────┐         ┌───────────┐
│ Rules  │         │ Summary   │   ← v1
│Adapter │         │ Adapter   │
└────────┘         └───────────┘
    │                    │
    ▼                    ▼
rules.yaml          summary.md


    (future adapters)
┌────────┐   ┌───────────┐
│  Docs  │   │  Skills   │
│Adapter │   │ Adapter   │
└────────┘   └───────────┘
ARCHITECTURE.md    Claude Code Skills
```

**Key property:** The AnalysisContext is computed once and persisted. Any adapter can be run independently afterwards — no re-analysis needed.

```bash
# Day 1: run analysis + rules
compass /repo --adapters rules

# Day 2: add summary without re-analyzing
compass /repo --adapters summary

# Force fresh analysis if codebase changed
compass /repo --adapters rules --reanalyze
```

---

## LLM Synthesis — CLI-based, no API credits required

LLM calls go through the CLI tool (`claude`, `codex`), not the API directly. This means no API credits are needed — only a CLI subscription.

Python orchestrates everything. When synthesis is needed, Python calls the CLI as a subprocess:

```python
result = subprocess.run(
    ["claude", "--print", "--output-format", "json", prompt],
    capture_output=True,
    text=True
)
```

### Multi-provider via plug-and-play

The synthesis layer is a thin abstraction (~10 lines per provider):

```python
# synthesis/providers.py

def synthesize(prompt: str, provider: str = "claude") -> str:
    if provider == "claude":
        return run(["claude", "--print", prompt])
    elif provider == "codex":
        return run(["codex", "--prompt", prompt])
```

```bash
compass /repo --adapters rules                     # default: claude
compass /repo --adapters rules --provider codex   # Codex CLI
```

Adding a new provider = implement one function.

### Structured output via JSON Schema

Claude's `--json-schema` flag enforces valid structured output — no manual parsing needed:

```bash
claude --print --json-schema '{"type":"object","properties":{"clusters":{...}}}' "$prompt"
```

Each adapter defines its own output schema. Python receives guaranteed-valid JSON.

### Cost control

```bash
claude --print --max-budget-usd 0.50 "$prompt"
```

Optional per-run budget cap. Configurable per adapter.

---

## Adapters

### Interface

Every adapter follows the same contract:

```python
class BaseAdapter:
    context_sections: list[str]   # which parts of AnalysisContext this adapter needs
    output_schema: dict           # JSON Schema for LLM output validation
    prompt_template: str          # path to prompts/<name>.md

    def run(self, context: AnalysisContext) -> AdapterOutput:
        ...
```

### Context Slicing

Adapters declare only what they need. The AnalysisContext is divided into sections:

| Section | Size (est.) | Content |
|---|---|---|
| `architecture` | ~1k tokens | Layers, clusters, hotspots |
| `git_patterns` | ~500 tokens | Trends, golden files, churn |
| `source` | ~4–5k tokens | repomix compressed code |

Adapter requirements:

| Adapter | architecture | git_patterns | source |
|---|---|---|---|
| RulesAdapter | ✓ | ✓ | ✓ |
| SummaryAdapter | ✓ | ✓ | — |
| DocsAdapter | ✓ | — | — |
| SkillAdapter | ✓ | — | — |

SummaryAdapter skips the `source` section — saves ~4k tokens per call automatically.

### v1 Adapters

**RulesAdapter** → `rules.yaml`
- Extracts coding conventions, error handling patterns, layer boundaries, testing patterns
- Structured as clusters (context + golden file) → atomic rules (id, rule, why)
- Only derives from observable code — hallucination guard enforced in prompt

**SummaryAdapter** → `summary.md`
- Produces an onboarding summary: architecture overview, key patterns, what to read first
- Written for a developer who has never seen the codebase

### Future Adapters

**DocsAdapter** → `ARCHITECTURE.md`, ADRs, etc.
- Generates missing documentation files from architecture analysis

**SkillAdapter** → Claude Code Skills
- Generates skills for code review and coding assistance
- Primary input: AnalysisContext; optional secondary input: rules.yaml if already generated

---

## Language Support

**Infrastructure:** fully language-agnostic (MCP graph analysis, repomix, git work on any repo)

**Prompts:** per-language templates, auto-detected from repo:

```
prompts/
  extract_rules.md          ← generic fallback
  extract_rules_ts.md       ← TypeScript / Node
  extract_rules_python.md   ← Python
  summary.md                ← generic
```

Override with `--lang typescript` if auto-detection is wrong.

---

## Prerequisites — auto-managed

The tool checks and sets up everything it needs before running:

1. `codebase-memory-mcp` installed? → install if missing
2. Repo indexed in codebase-memory-mcp? → run `index_repository` if not
3. repomix available? → install if missing
4. CLI provider available (`claude` / `codex`)? → error with install instructions if not

No manual setup required from the user.

---

## Output Structure

All output goes into `.compass/` inside the target repo (add to `.gitignore`):

```
target-repo/
└── .compass/
    ├── analysis_context.json   ← persisted analysis (with repo hash for staleness check)
    └── output/
        ├── rules.yaml
        ├── summary.md
        ├── ARCHITECTURE.md     (future)
        └── skills/             (future)
```

Staleness: `analysis_context.json` stores a hash of the repo state. If the hash differs on next run, the user is warned and can choose to re-analyze.

---

## CLI

```bash
# Run specific adapters
compass /path/to/repo --adapters rules
compass /path/to/repo --adapters rules,summary
compass /path/to/repo --adapters all

# Provider selection
compass /path/to/repo --adapters rules --provider claude     # default
compass /path/to/repo --adapters rules --provider codex

# Force fresh analysis
compass /path/to/repo --adapters summary --reanalyze

# Language override
compass /path/to/repo --adapters rules --lang python

# Budget cap
compass /path/to/repo --adapters all --max-budget 1.00
```

---

## Configuration

`.compass/config.yaml` (project-level) or `~/.compass/config.yaml` (global):

```yaml
default_provider: claude
default_model: claude-sonnet-4-6
max_budget_usd: 1.00
lang: auto
```

---

## Distribution

Internal tool. No package registry.

```bash
git clone <repo>
cd compass
pip install -e .
compass /path/to/target-repo --adapters rules
```

---

## Non-Goals

- **Not a code writer** — does not generate or scaffold code
- **Not interactive** — no chat, no REPL. Runs through, produces files, exits
- **Not a linter or formatter**
- **Not a PR review tool**
- **Not a dependency manager**
- **Not a monolith** — everything is modular; adapters are independent units
- **Not a replacement for docs the team should write** — it fills gaps, not responsibilities

---

## Roadmap

### v1 — Foundation
- [ ] Python project setup + CLI entry point (`compass`)
- [ ] Collectors: codebase-memory-mcp, repomix, git
- [ ] AnalysisContext schema + persistence + staleness check
- [ ] Prerequisites auto-check + setup
- [ ] `claude --print` synthesis provider
- [ ] RulesAdapter → `rules.yaml`
- [ ] SummaryAdapter → `summary.md`

### v2 — Extend
- [ ] `codex` synthesis provider
- [ ] DocsAdapter → `ARCHITECTURE.md`
- [ ] Language-specific prompt templates (TS, Python)
- [ ] Context slicing per adapter

### v3 — Polish
- [ ] SkillAdapter → Claude Code Skills
- [ ] Optional direct API provider (for those with credits)
- [ ] Prompt Caching for shared-context adapter runs
