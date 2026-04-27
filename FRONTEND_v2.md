# Frontend — Consolidated Reference

> **Status:** Semi-final draft — for team review
> **Replaces:** `FRONTEND.md` (architecture stub) + UX research in `research/`
> **Stack:** Next.js + TypeScript
> **Mockup:** `research/Mockup/compass_mockup_v2.html`

---

## The Two Users

**The new developer** — does not open a YAML file on day one. Needs to feel capable, not overwhelmed. The tool must orient them, not dump information at them.

**The business** — needs juniors productive faster. The real cost of onboarding is senior dev hours burned on questions that should not need to be asked.

---

## UX Vision

The UI answers the questions a new dev actually has on day one:
- What is this codebase and how is it structured?
- What are the rules and why do they exist?
- What should I read first?
- What should I never touch without understanding first?

**Layout:** Bento grid — 3-column card grid, one card per rule cluster. Each card shows the cluster name, rule count, a short context description, and its `golden_file` as a clickable link. Clicking a card expands the rules panel below. See `research/Mockup/compass_mockup_v2.html` for reference.

**The design brief:** Build something a new developer would screenshot and send to their team chat on their first day.

---

## Trust

Trust features that must be in the UI:
- every rule links to the file it was derived from (`golden_file`). In the UI this becomes a one-click link to the actual source code. The new dev can verify any rule in seconds.
- Every rule shows its `golden_file` as a clickable link — already present at cluster level in `rules.yaml`
- `confidence` (1–3) rendered as a visual signal — rules from many files feel different from rules from one file
- Gaps shown explicitly — "we did not find a clear convention for X" rather than a hallucinated rule

---

## Backend Architecture

### Runner separation
**Done.** `cli.py` and the future API layer both call `runner.py`. `runner.py` has no CLI knowledge.

```
cli.py      ← parses args, calls Runner
runner.py   ← core orchestration
api/        ← FastAPI, calls the same Runner
```

The `api/` layer is not yet built — it is the next step that makes a frontend possible.

### What already fits
The current architecture is already well-positioned for a frontend — no changes needed to these:
- `storage/` isolation — job state slots in naturally
- Structured JSON/YAML outputs — directly servable
- `providers/` abstraction — no changes required
- Two-phase design — maps cleanly to an async job model (Phase 1 = collecting, Phase 2 = synthesizing)

### Job model
**Open.** Analysis takes seconds to minutes. The frontend needs status tracking:

```
queued → collecting → synthesizing → done
```

`storage/` is the natural home for job state. Not yet implemented.

### Progress reporting
**Open.** FastAPI sends live updates via SSE (Server-Sent Events). The Next.js frontend listens and renders a progress indicator. No polling.

```
FastAPI (Python) → knows pipeline state → sends SSE
Next.js (browser) → receives SSE → updates UI
```

---

## Schema Status

What the frontend reads — current state of each data contract.

### `analysis_context.json`
- `file_scores` — done (`path`, `churn`, `age`, `centrality`, `cluster_id`, `coupling_pairs`)
- `coupling_pairs` — done (`file_a`, `file_b`, `degree`)
- `confidence` — open, not yet in schema
- `gaps` — open, not yet in schema

### `rules.yaml`
- `id`, `rule`, `why`, `example` — schema locked and validated
- `golden_file` — schema locked, present at cluster level
- `confidence` — open, not yet in schema
- `explain` — open, not yet in schema (plain English explanation for new devs)
- Note: RulesAdapter not yet built — schema is defined, file not yet produced by pipeline

### `summary.json`
- Schema locked: `repo_name`, `generated_at`, `what_it_does`, `read_first`, `stable`, `hotspots`, `clusters`
- Note: SummaryAdapter not yet built — schema is defined, file not yet produced by pipeline

---

## Open Items

| Item | Owner | Status |
|---|---|---|
| FastAPI layer | TBD | open |
| Job model + state tracking in `storage/` | TBD | open |
| SSE progress reporting | TBD | open |
| `--ui` flag reserved in CLI | TBD | open — not in parser yet, no placeholder |
| `confidence` field in `analysis_context.json` | Team 1 | open |
| `gaps` field in `analysis_context.json` | Team 1 | open |
| `confidence` field in `rules.yaml` | Team 2/3 | open |
| `explain` field in `rules.yaml` | Team 2/3 | open |
| Frontend ownership | Whole team | undecided |
| Local only vs. committed to repo | Whole team | undecided |

---

## Tech Stack

**Next.js + TypeScript** — to be confirmed with team.

Next.js is a React framework with a built-in server and file-based routing. Pages like `/rules`, `/summary`, and `/architecture` are created by adding files to the `pages/` directory — no manual routing needed.

TypeScript allows the schemas from `analysis_context.json` and `rules.yaml` to be defined as interfaces. If a field is renamed or removed in the backend, the compiler catches it immediately — no silent runtime failures.

- `npm run dev` — local development server with live reload
- `npm run build` — compiles TypeScript to JavaScript for production

The schema contracts above map directly to TypeScript interfaces. Locking the schemas locks the types.
