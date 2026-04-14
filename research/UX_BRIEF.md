# Compass — UX Brief

> **Team 4**
> **Author:** Stuart McLean
> **Status:** In progress — foundational positions captured, detail to follow
> **Feeds into:** VISIONS.md, BRAINSTORM.md, future front end architecture decisions

---

## The position nobody has written down yet

Every document in this project stops at the file output. `rules.yaml`. `summary.md`. Files in a `.compass/` folder.

**That is the pipeline output. It is not the product.**

The files are the data layer — inputs for machines, future adapters, and developers who want to extend Compass. What is missing from every current spec is the experience layer: the thing a human with feelings about their first week at a new job actually interacts with.

This document defines that layer.

---

## Two users, two needs

### The new dev
Does not open a YAML file on day one. Is already anxious. Already questioning whether they belong here. Already aware they are in everyone's way.

What they need is not a document. They need to feel capable enough to actually do the job. A wall of generated rules is not a UX. It is just a different kind of overwhelming.

### The business
Needs juniors productive faster. The real cost of onboarding is not the new dev's confusion — it is the senior dev hours burned answering questions that should not need to be asked, the mistakes made before conventions are understood, the six-month lag before someone is genuinely contributing.

The business does not need a dashboard or a mandate. It needs the tool to work well enough that the new dev tells the next new dev about it.

---

## Distribution hypothesis

**Compass succeeds bottom-up or not at all.**

The new dev discovers it, runs it, has a genuinely better first week. They tell the next person who joins. Word spreads inside the org without anyone mandating it.

This is how Slack spread. How Figma spread. How Notion spread. The product earns its place by being the kind of thing someone screenshots and sends to their team chat unprompted.

**That moment of "oh" is the entire marketing strategy.**

The UX bar is not "useful." It is "compelling enough to share." Those are different bars and the second one is higher.

Organisations that force-feed tools on people enforce the problem the tool is trying to fix. Compass must be discovered, not mandated.

---

## What the experience layer should be

The direction: **interactive, visual, navigable, human.**

Think bento box layout. Flow. Diagrams. Something that makes the codebase feel like a place you can orient yourself in, not a wall of text to decode.

The experience should answer the questions a new dev actually has on day one:

- What is this codebase and how is it structured?
- What are the rules and why do they exist?
- What should I read first?
- What should I never touch without understanding first?
- What is probably going to trip me up?

---

## Static files vs. interactive UI

### Option A — Static files only (MVP)
```
compass runs → rules.yaml + summary.md → done
```
**Pros:** simplest to build, works offline, files live in the repo and are versioned.
**Cons:** nobody reads long markdown files. No "oh" moment.

### Option B — Local web UI (recommended for v2)
```
compass /repo --adapters rules,summary --ui
→ Python starts local server → browser opens at localhost:3000
```
Technically: Python's built-in `http.server`. No Node, no React, no build step. Plain HTML + CSS + JavaScript reading directly from `analysis_context.json`.

What the UI does:
- Rules rendered as bento-box cards — one card per cluster, clickable, expandable
- Each card links directly to its `golden_file` — one click to the source code
- Confidence indicators visible without being technical
- Summary at the top as human entry point, rules below to navigate

**Pros:** the "oh" moment. Navigable, visual, human. `golden_file` becomes a clickable link, not an abstract filename.
**Cons:** more to build. Local only — not shareable as a link yet.

The `--ui` flag is opt-in — CI environments and servers don't get a browser they don't want.

---

## Trust is a design problem

Source citations, confidence signals, and honest gaps are not features — they are the foundation of whether anyone uses this tool at all. See Research question 3 in COMPETITIVE_ANALYSIS.md for the data.

**Trust features that belong in the experience layer:**
- Every rule shows which file it came from — one tap to the actual code
- Rules observed across many files feel different from rules derived from one example — the UI reflects this without being technical
- "We did not find a clear convention for X" is better than a hallucinated rule — surface gaps, don't paper over them

---

## Summary adapter — open questions

The summary adapter is the only current output designed for humans, not machines.

**Format** — `summary.md` renders fine in any UI. Markdown stays as the single output format. No JSON needed until the UI exists.

**Personalisation** — a beginner needs context and explanations. An intermediate dev needs to see the unusual patterns immediately. A `--level` flag could solve this:
```bash
compass /repo --adapters summary --level beginner
compass /repo --adapters summary --level intermediate
```

**Staleness** — the `analysis_context.json` already stores a repo hash. If the hash differs on next run, surface this directly in the output:
```
⚠️  Generated 2026-04-01. Significant changes since then (47 commits, 12 files).
    Run `compass --adapters summary --reanalyze` to update.
```

---

## Open questions for the team

- **What is the minimum viable "oh" moment?** What is the smallest version of the experience layer that still makes someone want to share it?
- **Does the front end get committed to the repo or stay purely local?** If it's not committed it risks losing influence in development decisions.
- **Should `summary.json` be generated alongside `summary.md` from day one** — even before the UI exists — so the data layer is ready when the UI arrives?
- **How do we design for anxiety without being patronising?** The user is anxious and new. The tone and framing of the output matters as much as the content.
- **At what point does a local UI become a reason to consider a hosted product?**

---

## The design brief in one sentence

> Build something a new developer would screenshot and send to their team chat on their first day.

That is the bar. Everything else follows from it.
