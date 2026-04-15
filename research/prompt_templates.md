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

| Adapter | architecture | git_patterns | patterns | docs | architecture_synthesis | FileSelector strategy |
|---|---|---|---|---|---|---|
| RulesAdapter | ✓ | ✓ | ✓ | ✓ | ✓ (v2) | low-churn + high-centrality + coupled pairs |
| SummaryAdapter | ✓ | ✓ | — | — | ✓ (v2) | high-centrality + hotspots, no raw source |
| DocsAdapter | ✓ | — | — | — | ✓ (v2) | entry points + dependency graph (lazy) |
| SkillAdapter | ✓ | ✓ | — | — | ✓ (v2) | low-churn files + rules.yaml if available |

`architecture_synthesis` is an empty slot in v1. It gets populated in v2 if a StructureAdapter is added (see below).

---

## The one-call problem — and how to handle it

A single LLM call producing a full summary has to do several epistemically distinct things at once: compress the codebase into plain English, infer what the coupling clusters reveal about module boundaries, identify gotchas from git signals, and rank files by usefulness to a new developer. These are different reasoning modes. When asked to do all of them in one flat instruction, models tend to produce evenly mediocre output across all sections rather than genuinely good output on any of them.

**The v1 fix: chain-of-thought within the prompt.** Instead of "write these sections," the prompt instructs the model to reason first and write second — explicitly, in sequence. The model identifies load-bearing files and coupling implications before it writes the orientation paragraph. The gotchas section is derived from pre-identified git signals, not inferred from scratch while writing prose.

**The v2 option: StructureAdapter as a named intermediate.** If quality testing shows the inferential sections (gotchas, architecture decisions) are consistently weak, the right fix is not a better prompt — it is splitting the work into two adapters:

```
analysis_context.json
        │
        ▼
StructureAdapter (Call 1)
        → architecture_synthesis.json
          (which files are load-bearing, what coupling clusters reveal,
           what churn profile implies — structured JSON, not prose)
        │
        ▼
SummaryAdapter (Call 2)
        → summary.md
          (now has pre-digested structural analysis as input —
           gotchas section renders a pre-computed list, not raw inference)
```

This keeps the one-call-per-adapter rule. It adds one adapter and one intermediate artifact. RulesAdapter, DocsAdapter, and SkillAdapter all benefit from `architecture_synthesis.json` too.

**The slot is reserved now.** `context_sections` in `adapters/base.py` should include `architecture_synthesis` as an optional field even in v1, left empty. This is cheap to do now and expensive to retrofit later.

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

All three templates use chain-of-thought sequencing: the model reasons through the signals before writing any prose. The analysis steps are the same across levels — what varies is the depth and language of the output sections.

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

Work through the following steps in order. Do not skip steps.

Step 1 — Identify the load-bearing files
From the file scores and centrality data, list the 3 files
that the rest of the codebase depends on most. For each, note
what would break if it changed.

Step 2 — Read the coupling clusters
From the coupling pairs, identify which files always change
together. What does that reveal about where the real module
boundaries are — not the folder names, but the actual
dependencies?

Step 3 — Surface the gotchas
From the git patterns, identify the 2-3 things most likely
to confuse or trip up someone new. Only include things with
evidence in the signals. Do not invent warnings.

Now use what you identified in Steps 1-3 to write the
following sections. Do not repeat the analysis — only the
output.

## What this codebase does
One paragraph. No acronyms. No layer names. What does this
software do for the person who uses it?

## How it is structured
Explain each folder. If there is an architectural pattern,
explain what it means in plain language before using the term.

## What to read first
3 files maximum. Use the load-bearing files from Step 1.
File path and one sentence on what reading it will teach you.

## What will trip you up
Use the gotchas from Step 3. Plain language. No jargon.

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

Work through the following steps in order. Do not skip steps.

Step 1 — Identify the load-bearing files
From the file scores and centrality data, list the 5 files
with the highest centrality. For each, note what architectural
role it plays.

Step 2 — Read the coupling clusters
From the coupling pairs, identify which files always change
together and what that implies about the actual module
boundaries vs the nominal folder structure. Flag any
boundary violations.

Step 3 — Surface the gotchas
From the git patterns, identify churn hotspots and coupling
pairs that indicate hidden complexity. What will a competent
dev assume that turns out to be wrong here?

Now use what you identified in Steps 1-3 to write the
following sections.

## What this codebase does
Two sentences maximum.

## How it is structured
Layers, boundaries, what can import what. Use the coupling
analysis from Step 2 to flag any violations.

## What to read first
5 files from Step 1. Path and one sentence each.
Highest centrality first.

## What will trip you up
Use the gotchas from Step 3. Assume the reader knows standard
patterns — only flag what deviates from them.

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

Work through the following steps in order. Do not skip steps.

Step 1 — Identify load-bearing abstractions
From centrality and coupling data, identify the files and
abstractions the entire system depends on. Note any that
have high churn — instability in a load-bearing file is
a risk signal.

Step 2 — Map the coupling risks
From the coupling pairs, identify hidden dependencies —
files with no import relationship but high co-change rate.
What does each imply about the architecture?

Step 3 — Surface non-obvious conventions
From the skeleton and git patterns, identify conventions
that are enforced but not visible in the folder structure
or naming. What would a senior dev assume that is wrong here?

Now write the following sections. Be dense. If a section
has nothing non-obvious to say, say so in one sentence.

## What this codebase does
One sentence.

## How it is structured
Primary pattern, layer boundaries. Use coupling analysis
from Step 2. Only surface what deviates from what a senior
dev would expect.

## What to read first
5 files from Step 1. Path and one clause each.

## What will trip you up
Coupling risks from Step 2 and non-obvious conventions
from Step 3 only.

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

Work through the following steps in order.

Step 1 — Identify the layer structure
From the architecture signals and dependency graph, map
the layers and what each is allowed to import. Flag any
violations you can observe.

Step 2 — Trace a request
Using actual file paths from the skeleton, trace one request
from entry point to persistence layer.

Step 3 — Identify gaps
What could not be determined from the available signals?
List explicitly — do not paper over uncertainty.

Now write the following sections using your analysis.

## Overview
What this system does and what problem it solves. 2-3 sentences.

## Layer structure
Use Step 1. Each layer, what lives there, import rules, violations.

## Key files
The 5-7 most central files by centrality score. Path and role only.

## Data flow
Use the request trace from Step 2. Actual file paths only.

## Known gaps
Use Step 3. Explicit list.

Rules:
- Derive only from what you observe in the context
- No hallucination. No invented architecture.
- Flag uncertainty rather than filling it with guesses.
```

---

## SkillAdapter template

SkillAdapter produces Claude Code skills. Its consumer is Claude Code, not a human and not the UI. Skills read from both `analysis_context.json` and `rules.yaml` if already generated. Section structure is defined by what a Claude Code skill requires to function.

SkillAdapter receives: `architecture` + `git_patterns` + grep_ast skeleton of low-churn files + `rules.yaml` if available.

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

Work through the following steps in order.

Step 1 — Map rules to observable patterns
For each rule in rules.yaml, identify what a violation looks
like in code. Use the skeleton as the source of examples —
do not write hypothetical code.

Step 2 — Identify intentional deviations
From the coupling signals and git patterns, identify patterns
that look wrong but are deliberate. These become the ignore list.

Now write the following sections.

## Trigger
When should this skill activate? Be specific.

## What to check
Use Step 1. Each check references a rule id from rules.yaml.

## What to flag
Exact violation patterns from Step 1. Skeleton examples only.

## What to ignore
Use Step 2. Patterns that look wrong but are intentional.

Rules:
- Every check must trace back to a rule id from rules.yaml
- No invented conventions
- Derive only from what you observe in the context
```

---

## Decisions required before any template is written

**Section structure** — the four H2 headings for SummaryAdapter templates are proposed above. Must be agreed by Team 2/3 and Team 4 before any template is drafted. Once locked, it cannot change without a UI update.

**Context variable names** — `{architecture}`, `{git_patterns}`, `{skeleton}`, `{rules_yaml}` must be agreed with Team 2 before templates are written. They map directly to the sections declared in `adapters/base.py` and the fields in `analysis_context.json`.

**architecture_synthesis slot** — `context_sections` in `adapters/base.py` should include `architecture_synthesis` as an optional field from v1, left empty. If quality testing shows inferential sections are consistently weak, StructureAdapter is the fix — and the slot makes that possible without a rewrite.

**Who decides:** Team 2/3 proposes, Team 4 confirms the UI can render it. Must happen before prompt templates are finalised.
