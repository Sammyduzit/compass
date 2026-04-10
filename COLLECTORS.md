# COLLECTORS.md — Compass Collector Stack

> **Status:** Proposed — pending team review  
> **Scope:** Collector layer, FileSelector, AnalysisContext shape  
> **Supersedes:** Collector and context sections of VISIONS.md  
> **Integration:** If accepted, the following sections of VISIONS.md should be updated to match: collector diagram, prerequisites check, roadmap v1 collector list, context slicing table.

---

## Final Collector Stack

### grep_ast
**Role:** Primary structure extraction — replaces ctags + repomix

Produces the condensed file skeleton (signatures, class shapes, parameter patterns) for selected files. Token-efficient, tree-sitter based, Python native. Every adapter consumes its output.

**Replaces possible usage of ctags** because ctags outputs a flat symbol list with no surrounding context — it tells you `AuthService` exists and where, but not what it looks like, what it accepts, or what it contains. The LLM receives names without structure. grep_ast produces the same symbol inventory plus the surrounding signature context, class membership, and nesting — enough for the LLM to understand patterns, not just enumerate identifiers.

**Replaces repomix (as primary source)** because repomix in full-repo mode packs everything into one blob regardless of relevance — a 10k LOC service produces ~40k tokens of noise. grep_ast on the same repo produces ~1-2k tokens of skeleton. More critically, repomix has no concept of importance — it gives every file equal weight. grep_ast is used after FileSelector has already ranked and chosen files, so its output is always scoped to what actually matters for the requesting adapter. repomix is retained only as a file fetcher (`--include` mode) for the rare case where an adapter needs raw file bodies rather than skeletons.

---

### ast-grep
**Role:** Pattern extraction for RulesAdapter specifically

Runs predefined structural queries across the repo to extract recurring constructs — error handling patterns, logging conventions, decorator usage, naming patterns. Feeds the `source` context section of RulesAdapter only.

---

### git log (custom Python parser)
**Role:** Importance scoring — replaces raw churn counting

Implements three signals from one `git log` pass:
- churn score per file (commit frequency × lines changed)
- logical coupling pairs (co-change percentage)
- code age per file (months since last touch)

Output feeds FileSelector scoring for every adapter. No external dependency, ~100 lines of Python.

**Replaces raw churn counting** because a single churn score per file is one-dimensional — it tells you a file changes frequently but not why or what it drags along with it. The logical coupling metric (derived from code-maat's methodology) adds a second dimension: when file A changes, what else always changes with it? This reveals hidden coupling that no static analysis tool can find — two files with no import relationship but 78% co-change rate indicates implicit dependency or a shared invariant. The code age signal adds a third dimension: files untouched for 14 months are stable conventions, not noise. Together these three signals let FileSelector make meaningfully different selections than churn alone would produce.

---

### FileSelector
**Role:** Curated file set per adapter — the core of context quality

Scores files using git signals + grep_ast cross-reference frequency, then selects the minimal relevant set per adapter before grep_ast renders their skeletons.

#### Why FileSelector exists

VISIONS.md describes context as static named slices (`architecture`, `git_patterns`, `source`) fed uniformly to every adapter. That model has a fundamental problem: both RulesAdapter and SummaryAdapter receive the same `source` section — the same files, the same weight, regardless of what each adapter actually needs to do its job.

LLMs don't struggle because of too little data. They struggle because of bad input selection. A generic packer optimizes for "fit as much as possible." FileSelector optimizes for "show only what matters for this specific task."

Without FileSelector:
```
repo → repomix → same blob  → RulesAdapter
                            → SummaryAdapter
```

With FileSelector:
```
repo → git signals + grep_ast centrality → FileSelector
                                               ├── RulesAdapter:   low-churn + high-centrality + coupled pairs
                                               └── SummaryAdapter: high-centrality + hotspots, no raw source
```

Each adapter gets a different set of files, selected for different reasons. This is where output quality jumps significantly — not in the prompts, not in the LLM, but in what gets fed in.

#### Selection criteria per adapter

| Adapter | Files selected | Reasoning |
|---------|----------------|-----------|
| RulesAdapter | low-churn + high-centrality + high-coupling-pairs | Low churn = stable conventions. High centrality = used everywhere, so patterns here are the real patterns. Coupled pairs shown together so the LLM sees the relationship. |
| SummaryAdapter | high-centrality + hotspots, zero raw source | Needs shape, not implementation. Directory structure + module relationships + git hotspots is enough. |
| DocsAdapter | entry points + dependency graph from codebase-memory-mcp | Needs directed dependency chains, not patterns. |
| SkillAdapter | low-churn + rules.yaml if exists | Stable files = conventions worth encoding as skills. rules.yaml feeds directly if already generated. |

#### What it looks like

```python
# collectors/file_selector.py

@dataclass
class FileScore:
    path: str
    churn: float        # 0–1, normalized across repo
    age_months: int
    centrality: float   # 0–1, cross-reference frequency from grep_ast
    coupling_pairs: list[str]  # files that co-change with this one

class FileSelector:
    def __init__(self, scores: list[FileScore]):
        self.scores = scores

    def for_rules(self, n: int = 8) -> list[str]:
        # stable (low churn) + central + bring coupling partners
        candidates = sorted(self.scores, key=lambda f: (f.churn, -f.centrality))
        selected = candidates[:n]
        # add coupling partners of selected files
        partners = {p for f in selected for p in f.coupling_pairs}
        return [f.path for f in selected] + list(partners)

    def for_summary(self, n: int = 6) -> list[str]:
        # most central + highest churn (hotspots) — no raw source bodies needed
        by_centrality = sorted(self.scores, key=lambda f: -f.centrality)
        by_churn = sorted(self.scores, key=lambda f: -f.churn)
        # interleave top results from both signals
        seen = set()
        result = []
        for f in by_centrality[:n] + by_churn[:n]:
            if f.path not in seen:
                seen.add(f.path)
                result.append(f.path)
        return result[:n]

    def for_skills(self, n: int = 6) -> list[str]:
        # most stable files — these are the conventions worth encoding
        return [
            f.path for f in sorted(self.scores, key=lambda f: f.age_months)[-n:]
        ]
```

FileSelector is the only component that knows about adapter intent. Collectors produce scores, adapters consume skeletons — FileSelector is the join between them.

---

### mcp2py + codebase-memory-mcp
**Role:** Dependency graph — DocsAdapter only, lazy

Only initialized when DocsAdapter is explicitly requested. Provides directed dependency graph that neither grep_ast nor git analysis can produce. Wired via mcp2py to avoid protocol boilerplate.

---

## Per-Adapter Context

| Adapter | FileSelector input | grep_ast | ast-grep | git signals | codebase-memory-mcp |
|---------|--------------------|----------|----------|-------------|---------------------|
| RulesAdapter | low-churn + high-centrality + high-coupling-pairs | selected files | pattern queries | churn + coupling + age | — |
| SummaryAdapter | high-centrality + hotspots | selected files | — | churn + age | — |
| DocsAdapter | — | entry points only | — | coupling graph | dependency graph |
| SkillAdapter | low-churn + rules.yaml | selected files | — | churn + age | — |

---

## Synthesis

| Provider | When | How |
|----------|------|-----|
| `claude --print` | v1/v2 default | subprocess, `--output-format json`, `--max-budget-usd` cap |
| `codex` | v2 alternative | same subprocess abstraction, one function in providers.py |
| Anthropic API | v3 opt-in | added as third branch, config-driven, no refactor needed |

---

## Prerequisites Check Order

```
1. grep_ast       → pip dependency, installed with Compass itself
2. ast-grep       → brew/cargo, checked at startup, clear error if missing
3. git            → always present, no check
4. claude CLI     → checked at startup, hard error with install instructions
5. codebase-memory-mcp + node  → checked only when DocsAdapter requested
```

v1 install is `pip install -e .` — zero Node, zero Java, zero MCP server.

---

## What was considered and rejected

| Tool | Reason rejected |
|------|-----------------|
| repomix (primary) | generic blob, no selection intelligence |
| ctags | flat symbol list, no context, superseded by grep_ast |
| code-maat JAR | Java dependency, same output achievable in ~100 lines Python |
| aider RepoMap | grep_ast is the useful part, full aider is too heavy |
| tree-sitter directly | grep_ast is already the wrapper, no need to go lower |
| LangChain / LlamaIndex | orchestration overhead for what is one prompt per adapter |
| vector DB / embeddings | overkill, AnalysisContext fits in a single LLM call |
| codebase-memory-mcp in v1 | prerequisite cost not justified until DocsAdapter |

---

## Tool Comparison: ast-grep vs grep_ast

They are complementary, not alternatives.

**ast-grep** — structural search CLI. Query-driven: you write a pattern, it finds all matches across the repo. Answers "what patterns exist."

**grep_ast** — tree-sitter wrapper that renders a condensed code skeleton per file. Answers "what is the shape of this codebase."

Token cost comparison on a typical 10k LOC service:

```
ctags output:        ~200 tokens   (symbols only, no context)
repomix full repo:   ~40k tokens   (everything)
grep_ast skeleton:   ~1-2k tokens  (structure with context)
```

---

## git Analysis: Logical Coupling (code-maat methodology)

The git collector implements the logical coupling metric from Adam Tornhill's *Your Code as a Crime Scene* directly in Python — no Java, no external JAR.

```python
# for every pair of files that ever changed in the same commit:
coupling_degree = shared_commits / total_commits_of_file_A
```

This reveals hidden coupling that static analysis cannot find. Two files with no import relationship but a high coupling percentage indicates implicit dependency, shared state, or an architectural boundary violation.

Used by:
- **RulesAdapter** — show coupled pairs together so the LLM sees the pattern in context
- **SummaryAdapter** — coupling clusters reveal actual module boundaries vs nominal folder structure
- **DocsAdapter** — behaviorally-derived architectural dependency map

---

## AnalysisContext Shape

Computed once, persisted to `.compass/analysis_context.json`. Any adapter runs independently from it afterwards.

```json
{
  "architecture": {
    "file_scores": [
      {
        "file": "src/auth/service.ts",
        "churn": 0.9,
        "age_months": 2,
        "centrality": 0.85
      }
    ],
    "coupling_pairs": [
      {
        "file_a": "src/auth/service.ts",
        "file_b": "src/user/repo.ts",
        "degree": 0.78
      }
    ],
    "skeleton": "...grep_ast output for selected files..."
  },
  "patterns": {
    "error_handling": "...ast-grep matches...",
    "naming": "...ast-grep matches..."
  },
  "git_patterns": {
    "hotspots": ["src/auth/service.ts"],
    "stable_files": ["src/core/base.ts"],
    "coupling_clusters": [
      ["src/auth/service.ts", "src/user/repo.ts"]
    ]
  }
}
```
