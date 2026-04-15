# Compass — Prompt Templates

> **Author:** Paula Schweppe, Team 4
> **Status:** Proposed — for Team 1/2/3 review
> **Feeds into:** DECIDED.md, prompts/templates/
> **Checked against:** team1/alternatives-research (COLLECTORS.md), team2/structure (STRUCTURE.md)

---

## How prompt templates fit into the pipeline

Compass runs in two strict phases. Phase 1 (Collectors) gathers data from the repo with zero LLM involvement and writes everything to `analysis_context.json`. Phase 2 (Adapters) is where prompt templates live.

Each adapter does three things:
1. Calls FileSelector at runtime to get its specific file set
2. Runs grep_ast on those files to produce a skeleton
3. Loads a prompt template, fills in the context sections it declared, and calls `claude --print`

**Important:** grep_ast runs in Phase 2, not Phase 1. Skeletons are not stored in `analysis_context.json`. What is stored are the scoring signals (churn, centrality, coupling pairs, patterns, docs) that FileSelector uses to make its selection. Each adapter selects a different file set and generates its own skeleton at runtime.

```
analysis_context.json  (scores, signals, patterns, docs)
        │
        ▼
   FileSelector  →  selects files per adapter
        │
        ▼
   grep_ast      →  skeleton of selected files
        │
        ▼
   Adapter fills template with its declared context sections
        │
        ▼
   claude --print
        │
        ▼
.compass/output/summary.md
```

Each adapter declares which sections of `analysis_context.json` it needs. Only those sections are passed to the LLM:

| Adapter | architecture | git_patterns | patterns | docs | FileSelector strategy |
|---|---|---|---|---|---|
| RulesAdapter | ✓ | ✓ | ✓ | ✓ | low-churn + high-centrality + coupled pairs |
| SummaryAdapter | ✓ | ✓ | — | — | high-centrality + hotspots, no raw source |
| DocsAdapter | ✓ | — | — | — | entry points + dependency graph (lazy) |
| SkillAdapter | ✓ | ✓ | — | — | low-churn files + rules.yaml if available |

---

## The section structure rule

The UI reads `summary.md` and renders it by section. This means every SummaryAdapter template — regardless of level — must produce the same four H2 headings. The content depth varies. The headings do not.

```
## What this codebase does
## How it is structured
## What to read first
## What will trip you up
```

This constraint does not apply to other adapters. DocsAdapter and SkillAdapter produce different output for different consumers — their section structure is defined by what those consumers need, not by what the UI renders.

---

## SummaryAdapter templates — three skill levels

The `--level` flag selects which template SummaryAdapter loads. One flag, one template, one LLM call, one output file. The level is invisible in the artifact.

SummaryAdapter receives: `architecture` + `git_patterns` + grep_ast skeleton of high-centrality and hotspot files. No raw source bodies — SummaryAdapter needs shape, not implementation.

---

### `summary_beginner.md`

```
You are writing an onboarding summary for someone new to
professional software development.

Architecture signals:
{architecture}

Git patterns (hotspots, stable files, coupling clusters):
{git_patterns}

Code skeleton (structure of the most central files):
{skeleton}

Write exactly these sections:

## What this codebase does
One paragraph. No acronyms. No layer names. What does this
software do for the person who uses it?

## How it is structured
Explain each folder. If there is an architectural pattern,
explain what it means in plain language before using the term.

## What to read first
3 files maximum. File path and one sentence on what reading
it will teach you.

## What will trip you up
Things that look wrong but are intentional. Derive from
gotchas and coupling signals in the context only.
Do not invent warnings.

Rules:
- No jargon without explanation
- Derive only from what you observe in the context
- If you are not sure, say so — do not fill gaps with guesses
```

---

### `summary_intermediate.md`

```
You are writing an onboarding summary for a developer who
knows how to code but has never seen this codebase.

Architecture signals:
{architecture}

Git patterns (hotspots, stable files, coupling clusters):
{git_patterns}

Code skeleton (structure of the most central files):
{skeleton}

Assume the reader understands standard patterns. Do not explain
what a repository pattern is — tell them how this team implements
it and why.

Write exactly these sections:

## What this codebase does
Two sentences maximum.

## How it is structured
Layers, boundaries, what can import what. Flag any boundary
violations that exist in the codebase.

## What to read first
5 files. Path and one sentence each. Highest centrality first.

## What will trip you up
Derive from coupling pairs, churn hotspots, and gotchas only.

Rules:
- No padding. Every sentence earns its place.
- Derive only from what you observe in the context.
```

---

### `summary_advanced.md`

```
You are briefing a senior developer who needs to be productive
within the hour.

Architecture signals:
{architecture}

Git patterns (hotspots, stable files, coupling clusters):
{git_patterns}

Code skeleton (structure of the most central files):
{skeleton}

Skip everything standard. Only surface what is non-obvious,
opinionated, or likely to cause a mistake.

Write exactly these sections:

## What this codebase does
One sentence.

## How it is structured
Primary pattern, layer boundaries, what is non-obvious or
opinionated. Skip anything a senior dev would assume by default.

## What to read first
5 files. Path and one clause each. Highest centrality first.

## What will trip you up
High churn + high centrality files. Coupled pairs with no
obvious import relationship. Enforced conventions not visible
in the folder structure.

Rules:
- Dense. No prose padding.
- Derive only from what you observe in the context.
- If there is nothing unusual in a section, say so in one
  sentence and move on.
```

---

## DocsAdapter template

DocsAdapter produces `ARCHITECTURE.md` for a repo that does not have one. Its consumer is a human reading markdown directly, not the UI. Section structure is defined by what an architecture document needs.

DocsAdapter receives: `architecture` + grep_ast skeleton of entry points + dependency graph from codebase-memory-mcp. codebase-memory-mcp is lazy — only initialised when DocsAdapter is explicitly requested. This is the only adapter that requires Node.

---

### `docs.md`

```
You are generating an ARCHITECTURE.md for a codebase
that does not have one.

Architecture signals:
{architecture}

Dependency graph:
{dependency_graph}

Code skeleton (entry points):
{skeleton}

Write exactly these sections:

## Overview
What this system does and what problem it solves. 2-3 sentences.

## Layer structure
Explain each layer, what lives there, and what it is allowed
to import. Derive from the layer boundaries in the context.

## Key files
The 5-7 most central files by centrality score. Path and role only.

## Data flow
Trace one request from entry point to persistence. Use actual
file paths from the context.

## Known gaps
Anything the analysis could not determine with confidence.
Surface gaps explicitly — do not paper over them.

Rules:
- Derive only from what you observe in the context
- No hallucination. No invented architecture.
- Flag uncertainty rather than filling it with guesses.
```

---

## SkillAdapter template

SkillAdapter produces Claude Code skills. Its consumer is Claude Code, not a human and not the UI. Skills read from both `analysis_context.json` and `rules.yaml` if already generated. Section structure is defined by what a Claude Code skill requires to function.

SkillAdapter receives: `architecture` + `git_patterns` + grep_ast skeleton of low-churn files + `rules.yaml` if available. Low-churn files are the ones that hold stable conventions — the right input for a skill that will enforce those conventions in review.

---

### `skill_review.md`

```
You are generating a Claude Code skill for reviewing code
in this codebase.

Architecture signals:
{architecture}

Git patterns:
{git_patterns}

Code skeleton (most stable files — these hold the real conventions):
{skeleton}

Existing rules:
{rules_yaml}

Write exactly these sections:

## Trigger
When should this skill activate? Be specific about the context
in which a developer would invoke it.

## What to check
Concrete checks derived from the rules. Each check must
reference a rule id from rules.yaml.

## What to flag
Exact patterns that violate the rules. Derive examples from
the skeleton only — do not write hypothetical examples.

## What to ignore
Patterns that look wrong but are intentional in this codebase.
Derive from the conventions and coupling signals in the context.

Rules:
- Every check must trace back to a rule id from rules.yaml
- No invented conventions
- Derive only from what you observe in the context
```

---

## Decisions required before any template is written

**Section structure** — the four H2 headings for SummaryAdapter templates are proposed above. Must be agreed by Team 2/3 and Team 4 before any template is drafted. Once locked, it cannot change without a UI update.

**Context variable names** — `{architecture}`, `{git_patterns}`, `{skeleton}`, `{rules_yaml}` must be agreed with Team 2 before templates are written. They map directly to the sections declared in `adapters/base.py` and the fields in `analysis_context.json`.

**Who decides:** Team 2/3 proposes, Team 4 confirms the UI can render it. Must happen before prompt templates are finalised.
