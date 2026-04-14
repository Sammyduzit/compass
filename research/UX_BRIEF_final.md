# Compass — UX Brief

> **Team 4**
> **Author:** Stuart McLean
> **Status:** Active — contains decisions that affect v1 architecture
> **Feeds into:** DECIDED.md, VISIONS.md, BRAINSTORM.md
> **Requires response from:** Team 1 (AnalysisContext schema), Team 2/3 (adapter outputs)

---

## Why this document needs to be read before v1 is built

Every current spec stops at the file output. `rules.yaml`. `summary.md`. Files in a `.compass/` folder.

The architecture decisions being made this week — AnalysisContext schema, adapter output formats, CLI interface — will either make an experience layer straightforward to add later, or make it expensive to retrofit. This is the window to get those decisions right.

This document does two things:
1. Identifies the specific v1 decisions that affect the future experience layer
2. Defines what that experience layer is and why it matters

---

## The decisions being made now that affect UX later

### 1. AnalysisContext schema — Team 1

The `analysis_context.json` schema is being defined now. If it is designed purely for LLM consumption, a front end will have to re-derive everything it needs from the raw output files.

**What needs to be true:** the schema should include UI-consumable fields from day one — not as extra work, but as a design constraint. Specifically:

- `golden_file` must be an absolute or repo-relative path that a UI can turn into a clickable link
- Confidence signals (how many files a rule was derived from) should be a field, not buried in prose
- Gaps and unknowns should be an explicit field, not absent from the output
- File scores, coupling pairs, and hotspots already exist in Team 1's proposed schema — these are exactly what a visual architecture diagram needs

**The cost of getting this wrong:** a front end has to parse markdown and YAML to reconstruct information that was available in the pipeline. Possible, but messy and fragile.

### 2. `summary.md` output format — adapter design

The SummaryAdapter produces `summary.md`. Markdown is fine for reading. It is not consumable by a UI without parsing.

**What needs to be true:** `summary.json` should be generated alongside `summary.md` from day one — even before any UI exists. The JSON is the data layer. The markdown is one rendering of it. This costs almost nothing to add at adapter build time and saves a significant retrofit later.

**The cost of getting this wrong:** when the UI arrives, someone has to write a markdown parser to extract structured data that was always available in the pipeline. That is wasted work.

### 3. CLI interface — `--ui` flag

The CLI interface is being designed now. Adding a `--ui` flag later is a minor change. Not designing for it at all means the flag gets deprioritised indefinitely.

**What needs to be true:** reserve `--ui` as a recognised flag in the CLI design, even if it is a no-op in v1. This signals that the experience layer is in scope, not an afterthought.

```bash
compass /repo --adapters rules,summary --ui
# v1: runs pipeline, opens browser to localhost:3000
# MVP: runs pipeline, outputs files (flag reserved but passive)
```

### 4. The `why` field on rules — non-negotiable

The `why` field in `rules.yaml` is currently part of the schema. It must stay. Rules without reasoning get ignored — this is confirmed by the trust research (65% of developers say AI misses context; rules without a why feel arbitrary). In the UI, `why` is what transforms a rule from a command into something a new dev actually internalises.

**What needs to be true:** `why` remains a required field in the rules schema. It is not optional, not droppable for token saving.

---

## The two users this tool serves

### The new dev
Does not open a YAML file on day one. Is already anxious. Already questioning whether they belong. Already aware they are in everyone's way.

What they need is not a document. They need to feel capable enough to actually do the job. A wall of generated rules is not a UX — it is just a different kind of overwhelming.

### The business
Needs juniors productive faster. The real cost of onboarding is not the new dev's confusion — it is the senior dev hours burned on questions that should not need to be asked, mistakes made before conventions are understood, the six-month lag before someone is genuinely contributing.

The business does not need a dashboard or a mandate. It needs the tool to work well enough that the new dev tells the next new dev about it.

**Our research confirms this is a documented, costly problem:**
- 78% of new developers find codebase navigation challenging or very challenging
- $8,000–$18,000 in diverted senior productivity per new hire over the first 2–3 months
- 36% of new developers say their top priority is introductory guides — the supply does not meet the demand

See COMPETITIVE_ANALYSIS.md for sources.

---

## Distribution hypothesis

**Compass succeeds bottom-up or not at all.**

The new dev discovers it, runs it, has a genuinely better first week. They tell the next person. Word spreads without anyone mandating it — this is how Slack, Figma, and Notion spread.

Organisations that force-feed tools on people enforce the problem the tool is trying to fix. Compass must be discovered, not mandated.

**That moment of "oh" is the entire go-to-market strategy. The UX bar is not "useful." It is "compelling enough to share."**

---

## What the experience layer looks like

The direction: **interactive, visual, navigable, human.**

Bento box layout. Flow. Diagrams. Something that makes the codebase feel like a place you can orient yourself in — not a wall of text to decode.

**Technically:** Python's built-in `http.server`. No Node, no React, no build step. Plain HTML + CSS + JavaScript reading directly from `analysis_context.json`. This is not a large engineering lift.

```
compass /repo --adapters rules,summary --ui
→ Python starts local server
→ browser opens at localhost:3000
→ new dev sees their codebase, not a file
```

**What the UI answers — the questions a new dev actually has on day one:**
- What is this codebase and how is it structured?
- What are the rules and why do they exist?
- What should I read first?
- What should I never touch without understanding first?
- What is probably going to trip me up?

**What it looks like:**
- Rules as bento-box cards — one card per cluster, clickable, expandable
- Each card links directly to its `golden_file` — one click to the actual source code
- Architecture shown as a navigable diagram, not a folder tree
- Summary at the top as human entry point, rules below to explore
- Confidence signals visible without being technical
- Gaps surfaced explicitly — "we couldn't find a clear convention for X"

---

## Trust is a design problem

96% of developers do not fully trust AI-generated output. The only mechanism that builds trust is provenance — every claim traceable to its source.

Compass already has the structural answer: `golden_file`. Every rule links to the file it came from. In the UI this becomes a clickable link. The new dev can verify any rule in seconds.

**This is Compass's trust advantage over every other automated tool in the market.** See COMPETITIVE_ANALYSIS.md — provenance per rule is uncontested.

Trust features that must survive into the UI:
- Every rule shows which file it came from — one tap to the actual code
- Rules derived from many files feel different from rules from one file — the UI reflects this
- Gaps are shown, not hidden — "we did not find a clear convention for X" is better than a hallucinated rule

---

## Open questions requiring team decisions

These are not rhetorical. They need answers before v1 ships.

| Question | Why it matters | Who decides |
|---|---|---|
| Does `summary.json` get generated alongside `summary.md` from day one? | Retrofitting is expensive. Doing it now costs almost nothing. | Team adapters |
| Is `--ui` reserved in the v1 CLI even as a no-op? | Signals it is in scope. Keeps the door open. | Team CLI |
| Is `golden_file` stored as an absolute path or repo-relative? | Determines whether a UI can make it a clickable link without extra work. | Team 1 schema |
| Is `why` a required field or optional in the rules schema? | Optional means it gets dropped under pressure. Required means it stays. | Team rules schema |
| Does the front end get committed to the repo or stay local only? | Local = personal tool. Committed = team artifact. Different products. | Whole team |

---

## The design brief in one sentence

> Build something a new developer would screenshot and send to their team chat on their first day.

That is the bar. The pipeline is in service of it. The files are in service of it. Everything is in service of it.
