# Compass — README for Humans

> **Author:** Stuart McLean, Team 4
> **Who this is for:** Anyone who just joined this project and has no idea what's going on
> **What this is not:** A technical spec. Go to VISIONS.md for that.

---

## What are we actually building?

Compass is a command-line tool that scans a codebase and produces a set of documents to help a new developer get up to speed — fast.

You run one command:

```bash
compass /path/to/repo --adapters rules,summary
```

And it produces:
- A **rules file** — the unwritten conventions of the codebase. How errors are handled. How files are named. What patterns the team always follows. Extracted from the actual code, not from documentation someone wrote and forgot to update.
- A **summary** — a plain English overview of the codebase. What it does, how it's structured, what to read first.

Eventually it will also produce an **interactive visual experience** — but more on that later.

---

## Why does this exist?

Starting on a new codebase is painful. Not because the code is bad — because the rules are invisible.

Every team has conventions. Ways of doing things. Patterns that everyone follows but nobody wrote down. A new developer spends weeks figuring these out by reading code, making mistakes, and interrupting the one senior dev who "knows everything."

That costs time. It costs money — research puts the senior dev productivity loss at $8,000–$18,000 per new hire over the first few months. And it costs the new developer something harder to measure: confidence. Impostor syndrome. The feeling of being in everyone's way.

Compass extracts those invisible rules from the code itself and puts them somewhere a new developer can actually find them.

---

## Who is on this project and what is each team doing?

**Team 1 — Janis & Martins: The Collectors**
They are building the data-gathering layer. Before any AI gets involved, Compass needs to scan the codebase and collect information about it — which files matter, how they relate to each other, what patterns appear in the code, what the git history reveals. Team 1 is deciding which tools do this and how.

**Team 2 & 3 — Michael, Abdelwahab: The Adapters and Prompts**
They are building the AI layer. Once the data is collected, it gets handed to an AI (Claude) with a specific prompt. The AI produces the output — the rules file, the summary. Team 2/3 are designing those prompts and the adapter code that handles the AI calls.

**Team 4 — Stuart & Paula: Research and UX**
That's us. We are doing two things. Paula is mapping the competitive landscape — what tools exist, where Compass sits in the market, what nobody else is doing. Stuart is defining the user experience — who this tool is actually for, what they need, and what the engineering team needs to account for now to make a good experience possible later.

---

## How does the pipeline actually work?

Think of it in two phases:

### Phase 1 — Data collection (no AI, no cost)
Compass scans the repo using a set of tools:

- **grep_ast** — reads the shape of the code. Not the full code — just the structure. Function signatures, class shapes, how things are organised.
- **ast-grep** — searches for recurring patterns across the whole repo. How does error handling work? What naming conventions appear everywhere?
- **Custom git parser** — reads the git history. Which files change the most? Which files always change together? Which files haven't been touched in a year (those are the stable, trusted ones)?
- **import_graph** — figures out which files are imported by the most other files. Those are the important ones — the ones that define how everything else works.

All of this gets combined into a single file: `analysis_context.json`. Think of it as Compass's understanding of the codebase — saved to disk so it doesn't have to be repeated.

**FileSelector** is the smart part: instead of sending everything to the AI, it picks only the files that actually matter for each specific task. Rules need stable, central files. Summaries need a different set. The AI gets signal, not noise.

### Phase 2 — AI synthesis (one call per output)
Each output is produced by one focused AI call:

- **RulesAdapter** — takes the analysis, calls Claude, gets back `rules.yaml`
- **SummaryAdapter** — takes the analysis (minus the raw source code, saving tokens), calls Claude, gets back `summary.md`

Each adapter is independent. You can re-run one without re-running the whole pipeline.

---

## What is the AnalysisContext?

It is the JSON file that sits between Phase 1 and Phase 2. It is the contract between the collectors and the adapters.

Think of it as a structured summary of everything Compass learned about the codebase — before any AI got involved. It contains:
- Which files are important and why (centrality, churn, coupling scores)
- The skeleton of the code (from grep_ast)
- The patterns found across the repo (from ast-grep)
- The git signals (hotspots, stable files, files that always change together)
- Any existing documentation found in the repo

It gets saved to `.compass/analysis_context.json` inside the target repo. If the codebase hasn't changed since last time, Compass skips Phase 1 entirely and goes straight to Phase 2.

---

## What is rules.yaml?

It is the main output. A structured file of coding conventions, organised into clusters.

Each cluster is a theme — error handling, dependency injection, testing patterns, etc. Each cluster contains:
- **context** — why this cluster exists, what problem it solves
- **golden_file** — the best example file in the codebase for this pattern
- **rules** — the specific rules, each with:
  - **id** — a unique identifier
  - **rule** — the rule itself, in plain English
  - **why** — the reasoning behind it
  - **example** — a code snippet showing right and wrong

The `why` field is not optional. Rules without reasoning get ignored.

---

## What is the experience layer and why does it matter?

Right now, Compass produces files. A developer runs it and gets `rules.yaml` and `summary.md` sitting in a folder.

Nobody reads YAML files on their first day.

The experience layer is what sits on top of those files — an interactive, visual interface that makes the codebase feel like a place you can explore, not a document you have to decode. Think navigable diagrams, clickable rules that link to the actual source code, a layout that answers the questions a new developer actually has.

**Why it matters for the engineering team:** the decisions being made right now — what goes into the AnalysisContext, what format the outputs use — will either make the experience layer easy to build later or expensive to retrofit. The UX Brief (also in the research folder) explains exactly which decisions those are.

---

## What is decided and what is still open?

**Locked (do not re-open):**
- The name is Compass
- The CLI is Python
- Two phases — collectors then adapters, never mixed
- v1 ships two outputs: rules.yaml and summary.md
- No package registry — distributed via git clone

**Open (still being worked out):**
- The exact AnalysisContext schema
- Whether summary.json gets generated alongside summary.md
- What the experience layer looks like and when it gets built
- Whether the tool stays local or eventually becomes a hosted product

---

## Where do I find things?

| Document | What it is |
|---|---|
| `DECIDED.md` | Locked decisions. Don't re-open these. |
| `VISIONS.md` | Full technical spec. Read this when you need the detail. |
| `BRAINSTORM.md` | Open questions. This is where to bring new ideas. |
| `PIPELINE.md` | Findings from the first pipeline run. What worked, what didn't. |
| `research/COMPETITIVE_ANALYSIS.md` | What tools exist in the market and where Compass sits. |
| `research/UX_BRIEF.md` | Who this is for, what the experience layer should be, what the engineering team needs to account for now. |
| `team1/COLLECTORS.md` | Team 1's proposed collector stack — the most technically detailed document in the repo. |

---

## The one sentence that matters

> Build something a new developer would screenshot and send to their team chat on their first day.

Everything else — the pipeline, the collectors, the adapters, the schema decisions — is in service of that.
