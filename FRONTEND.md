# Frontend Integration — Architecture Notes

> **Status:** Future consideration — not in scope for v1
> **Purpose:** Document what needs to be in place before a frontend can be added, so these decisions can be made deliberately during final planning.

---

## Current State

Compass is designed as a run-and-exit CLI tool. A frontend is possible but not trivial with the current architecture — it would require partial refactoring if not prepared for upfront.

---

## The One Change That Enables Everything

**Decouple the pipeline runner from the CLI entry point.**

```
compass/
├── cli.py      ← thin wrapper — parses args, calls Runner
├── runner.py   ← core orchestration — no CLI knowledge
└── api/        ← FastAPI — calls the same Runner
```

`cli.py` and a future API layer both call `runner.py`. This is the clean seam. If `runner.py` is separated from day one, a frontend is an addon later — not a refactor.

---

## What Else Would Be Needed

**Job model** — analysis takes seconds to minutes. A frontend needs status tracking (`queued → collecting → synthesizing → done`). `storage/` is the natural home for job state.

**Progress reporting** — SSE or WebSocket so the frontend receives live updates instead of blind polling.

**HTTP layer** — thin FastAPI layer on top of Runner:
- `POST /analyze` → start job
- `GET /jobs/{id}` → status + progress
- `GET /jobs/{id}/output` → results

---

## What Already Fits

- `storage/` isolation — job state slots in naturally
- Structured JSON/YAML outputs — directly servable
- `providers/` abstraction — no changes needed
- Two-phase design — maps cleanly to async job model (Phase 1 = collecting, Phase 2 = synthesizing)

---

## Recommendation

Do not implement the API or job model in v1. Do ensure `runner.py` is cleanly separated from `cli.py` from the start — that single decision keeps the frontend path open without adding any complexity to v1.
