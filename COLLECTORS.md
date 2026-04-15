# COLLECTORS.md — Compass Collector Stack

> **Status:** Proposed — pending team review  
> **Scope:** Collector layer, FileSelector, AnalysisContext shape  
> **Proposes changes to:** Collector and context sections of VISIONS.md  
> **Integration:** If accepted, the following sections of VISIONS.md should be updated to match: collector diagram, prerequisites check, roadmap v1 collector list, context slicing table.

---

## Final Collector Stack

### grep_ast
**Role:** Primary structure extraction — replaces ctags + repomix

Produces the condensed file skeleton (signatures, class shapes, parameter patterns) for selected files. Token-efficient, tree-sitter based, Python native. Every adapter consumes its output.

**Replaces ctags** because ctags outputs a flat symbol list with no surrounding context — it tells you `AuthService` exists and where, but not what it looks like, what it accepts, or what it contains. The LLM receives names without structure. grep_ast produces the same symbol inventory plus the surrounding signature context, class membership, and nesting — enough for the LLM to understand patterns, not just enumerate identifiers.

**Proposed replacement for repomix as primary source.** The correct comparison is grep_ast skeleton vs. `repomix --compress` on the same FileSelector-chosen files — not against full-repo mode. That comparison is an open question: does grep_ast's condensed skeleton give better signal than repomix's compressed source for the same file set? The hypothesis is yes — grep_ast omits implementation bodies and focuses on structure, which is what RulesAdapter and SummaryAdapter actually need. But this should be validated against the existing pipeline output before treating it as settled. repomix is retained as a file fetcher (`--include` mode) for cases where an adapter needs raw file bodies rather than skeletons.

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

### import_graph (custom Python parser)
**Role:** Centrality scoring — required input for FileSelector

Parses import statements from source files across the repo, builds a directed import graph, and computes a per-file centrality score (PageRank or in-degree). This is a discrete pipeline step — grep_ast produces a text skeleton, not a graph, and cannot produce centrality scores on its own.

```python
# collectors/import_graph.py

import ast
from pathlib import Path
from collections import defaultdict

def build_import_graph(repo_path: str) -> dict[str, float]:
    """
    Returns a dict of file_path → centrality score (0–1, normalized).
    Higher = more files import this file.
    """
    graph: dict[str, list[str]] = defaultdict(list)

    for path in Path(repo_path).rglob("*.py"):
        try:
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    # resolve to file path, add edge
                    ...
        except SyntaxError:
            continue

    # compute in-degree centrality
    in_degree = defaultdict(int)
    for _src, targets in graph.items():
        for t in targets:
            in_degree[t] += 1

    max_degree = max(in_degree.values(), default=1)
    return {f: in_degree[f] / max_degree for f in in_degree}
```

TypeScript/JS import resolution uses ast-grep structural queries — `import $_ from '$SOURCE'` and `require('$SOURCE')` — to extract import edges without writing a custom parser. The graph build and centrality computation (networkx) are the same regardless of language. The output contract (`file → float`) is identical across languages.

#### Architectural decision: import_graph implementation approach

Three options were evaluated for how to extract import edges and compute centrality:

**Option A — codebase-memory-mcp + ast-grep** *(selected)*
codebase-memory-mcp provides centrality + semantic clusters + architectural layers. ast-grep handles the structural pattern queries it already does for RulesAdapter. The two are complementary: codebase-memory-mcp answers "how is this codebase structured and which files matter", ast-grep answers "what patterns exist in those files."
Node.js dependency is not a new constraint: codebase-memory-mcp is already planned for DocsAdapter, so Node and `index_repository` will be present for any user running a full analysis. Promoting it to core changes when it is required, not whether it is required.
Semantic clustering directly addresses the three failure modes that pure behavioral signals cannot cover:

1. **Low-traffic domains with important conventions.** A payment or billing module that rarely changes (low churn), isn't widely imported (low centrality), and doesn't co-change with much else ranks near the bottom on every behavioral signal. Semantic clustering identifies it as a distinct cluster and ensures representation — domain-specific conventions in quieter areas of the codebase are sampled rather than dropped.

2. **New code encoding where the codebase is heading.** A recently added module has no coupling history, low churn (not enough time), and low centrality (not yet imported widely). All three behavioral signals rank it low. Semantic clustering finds it by similarity, not by history — new architectural patterns get surfaced even before they have behavioral evidence.

3. **Domain completeness across isolated layers.** The category coverage constraint handles *file type* coverage (DTOs, tests, handlers). It does not handle *domain* coverage — ensuring you sample from auth, billing, notifications, etc. Semantic clustering explicitly surfaces one representative per domain cluster, preventing over-representation of the highest-traffic module.

**Option B — ast-grep for edge extraction + networkx for graph math**
No new external dependencies beyond pip. Rejected because it produces centrality only — all three domain coverage failure modes above remain open, and since the Node.js dependency is present anyway via DocsAdapter, the tradeoff is no longer justified.

**Option C — tree-sitter Python bindings + networkx inside Compass**
Same output as Option B, significantly more build effort. Rejected on the same grounds as B, with additional cost.

**Decision: Option A (codebase-memory-mcp + ast-grep).** codebase-memory-mcp handles centrality and semantic clustering. ast-grep handles structural pattern queries. Node.js is not an added dependency — it is already required for DocsAdapter. This combination closes all three domain coverage failure modes that behavioral signals alone cannot address.

---

### FileSelector
**Role:** Curated file set per adapter — the core of context quality

Scores files using git signals + grep_ast cross-reference frequency, then selects the minimal relevant set per adapter before grep_ast renders their skeletons.

#### Why FileSelector exists

VISIONS.md describes context as static named slices (`architecture`, `git_patterns`, `source`) fed uniformly to every adapter. That model has a fundamental problem: both RulesAdapter and SummaryAdapter receive the same `source` section — the same files, the same weight, regardless of what each adapter actually needs to do its job.

LLMs don't struggle because of too little data. They struggle because of bad input selection. A generic packer optimizes for "fit as much as possible." FileSelector optimizes for "show only what matters for this specific task."

Without FileSelector:
```
repo → repomix → same blob → RulesAdapter
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
|---|---|---|
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

#### Category coverage constraint

Signal-based selection alone can reproduce a known quality failure: files with medium churn and medium centrality (e.g. DTOs, validation schemas, test pairs) get systematically underrepresented because no single signal ranks them highly, even though they are essential for a complete picture of the codebase's conventions.

FileSelector applies a coverage constraint pass after signal-based scoring. After the initial ranked selection, it checks that at least one file from each required category is present, and fills gaps from the remaining scored files if not.

```python
# Required categories per adapter — auto-detected from file naming patterns
RULES_COVERAGE: dict[str, str] = {
    "dto":        r"(dto|schema|model)\.(ts|py)$",
    "validation": r"(valid|guard|pipe)\.(ts|py)$",
    "test":       r"\.(spec|test)\.(ts|py)$",
    "handler":    r"(controller|handler|route)\.(ts|py)$",
}

def apply_coverage(
    selected: list[str],
    all_scores: list[FileScore],
    categories: dict[str, str],
) -> list[str]:
    import re
    covered = set()
    for path in selected:
        for cat, pattern in categories.items():
            if re.search(pattern, path):
                covered.add(cat)

    result = list(selected)
    for cat, pattern in categories.items():
        if cat not in covered:
            # find highest-scored file matching this category
            for score in all_scores:
                if re.search(pattern, score.path) and score.path not in result:
                    result.append(score.path)
                    break

    return result
```

Categories are defined per adapter and can be extended via language-specific templates (e.g. a Python repo has different naming patterns than a TypeScript repo).

**Known limitation:** The regex patterns match file names by suffix convention. Non-standard naming will be silently missed — e.g. `user.types.ts` does not match the `dto` pattern, and test files in a `tests/` directory without a `.spec` or `.test` suffix won't match the `test` pattern. Repos that deviate from the assumed naming conventions will produce incomplete category coverage without any warning. This is a documented tradeoff: the patterns cover the common case well enough to fix the systematic underrepresentation problem, but they cannot guarantee exhaustive coverage for every naming style. Per-language template overrides are the intended extension point.

---

### mcp2py + codebase-memory-mcp
**Role:** Centrality, semantic clustering, and dependency graph — core collector

Runs for all adapters. Provides centrality scores, semantic file clusters, and architectural layers (used by FileSelector for all adapters), plus directed dependency graph (used by DocsAdapter). Wired via mcp2py to avoid protocol boilerplate. Requires Node.js and an `index_repository` step — this is a known prerequisite, not an added cost, since DocsAdapter already required it.

---

### docs_reader
**Role:** Explicit rules extraction — fills gap left by dropping codebase-context

Scans the repo for known documentation files and extracts their content into the `docs` context section. Targets: `CONTRIBUTING.md`, `ADR` files, `ARCHITECTURE.md`, `README.md` (root only), `.cursor/rules`, `.claude/rules`.

This addresses a real gap: style rules and team conventions that are explicitly written down but not visible in code signatures will be missed by RulesAdapter if only source files are analyzed. `get_style_guide` from codebase-context covered this; docs_reader is its replacement without the MCP dependency.

```python
# collectors/docs_reader.py

KNOWN_DOC_PATTERNS = [
    "CONTRIBUTING.md",
    "ARCHITECTURE.md",
    "README.md",          # root only
    "docs/adr/*.md",
    "docs/decisions/*.md",
    ".cursor/rules",
    ".claude/rules",
]

def collect_docs(repo_path: str) -> dict[str, str]:
    """Returns a dict of filename → content for all found doc files."""
    ...
```

Output feeds the `docs` context section. RulesAdapter declares it as an input alongside `architecture` and `git_patterns`.

**Note on semantic git signals:** codebase-context also provided git gotchas — decision records and known pitfalls extracted from commit messages and PR patterns. This is a semantic signal distinct from churn/coupling/age. It is not covered by the custom git log parser and is out of scope for this proposal. If the team considers it valuable, it warrants a separate collector (`git_semantics`) in a future iteration.

---

## Per-Adapter Context

| Adapter | FileSelector input | grep_ast | ast-grep | git signals | docs_reader | codebase-memory-mcp |
|---|---|---|---|---|---|---|
| RulesAdapter | low-churn + high-centrality + high-coupling-pairs | selected files | pattern queries | churn + coupling + age | ✓ | centrality + semantic clusters |
| SummaryAdapter | high-centrality + hotspots | selected files | — | churn + age | — | centrality + semantic clusters |
| DocsAdapter | — | entry points only | — | coupling graph | — | centrality + semantic clusters + dependency graph |
| SkillAdapter | low-churn + rules.yaml | selected files | — | churn + age | — | centrality + semantic clusters |

---

## Synthesis

| Provider | When | How |
|---|---|---|
| `claude --print` | v1/v2 default | subprocess, `--output-format json`, `--max-budget-usd` cap |
| `codex` | v2 alternative | same subprocess abstraction, one function in providers.py |
| Anthropic API | v3 opt-in | added as third branch, config-driven, no refactor needed |

---

## Prerequisites Check Order

```
1. grep_ast       → pip dependency, installed with Compass itself
2. import_graph   → pip dependency, installed with Compass itself
3. docs_reader    → pip dependency, installed with Compass itself
4. ast-grep       → brew/cargo, checked at startup, clear error if missing
5. git            → always present, no check
6. claude CLI     → checked at startup, hard error with install instructions
7. codebase-memory-mcp + node  → checked at startup, required for all adapters
```

v1 install is `pip install -e .` + Node (required for codebase-memory-mcp). Zero Java, zero MCP server beyond codebase-memory-mcp.

---

## What was considered and rejected

| Tool | Reason rejected |
|---|---|
| repomix (primary) | generic blob, no selection intelligence |
| ctags | flat symbol list, no context, superseded by grep_ast |
| code-maat JAR | Java dependency, same output achievable in ~100 lines Python |
| aider RepoMap | grep_ast is the useful part, full aider is too heavy |
| tree-sitter directly | grep_ast is already the wrapper, no need to go lower |
| LangChain / LlamaIndex | orchestration overhead for what is one prompt per adapter |
| vector DB / embeddings | overkill, AnalysisContext fits in a single LLM call |
| networkx-only import_graph (Option B/C) | centrality only — semantic clustering gaps not justified when Node.js is present anyway |

---

## Tool Comparison: ast-grep vs grep_ast

They are complementary, not alternatives.

**ast-grep** — structural search CLI. Query-driven: you write a pattern, it finds all matches across the repo. Answers "what patterns exist."

**grep_ast** — tree-sitter wrapper that renders a condensed code skeleton per file. Answers "what is the shape of this codebase."

Token cost comparison on a typical 10k LOC service:

```
ctags output:                        ~200 tokens   (symbols only, no context)
repomix --compress (FileSelector):   ~2-4k tokens  (compressed source, scoped)
grep_ast skeleton (FileSelector):    ~1-2k tokens  (structure only, no bodies)
```

The honest comparison is grep_ast vs. `repomix --compress` on the same FileSelector-chosen files — not against full-repo mode. grep_ast's advantage is that it omits implementation bodies entirely, which is the right tradeoff for structure-oriented adapters. Whether that produces better LLM output than compressed source for the same files is an open question to validate against the existing pipeline.

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

**What is and isn't stored:** AnalysisContext stores the *inputs* to FileSelector — scores, coupling pairs, signals, patterns, docs. It does not store grep_ast skeletons. Skeleton output is not stored because each adapter selects a different file set: storing a single skeleton would require picking one adapter's files as canonical, which is wrong. Instead, each adapter calls FileSelector at runtime (Phase 2) to get its file set, then runs grep_ast on those files to produce its own skeleton. This means grep_ast runs during Phase 2, not Phase 1. The cost is low (grep_ast is fast) and it ensures each adapter sees exactly the skeleton it needs.

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
    ]
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
  },
  "docs": {
    "CONTRIBUTING.md": "...extracted content...",
    "docs/adr/001-use-fastify.md": "...extracted content..."
  }
}
```
