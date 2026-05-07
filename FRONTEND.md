# Frontend — v2 Architecture

> **Status:** Planned for v2 — not in scope for v1 CLI
> **Reference research:** `research/` — competitive analysis, UX brief, build roadmap

---

## Decision: No local `--ui` viewer

The CLI tool outputs `.md`, `.yaml`, and `.json` files that developers open directly. A local browser viewer adds complexity without meaningful benefit. The v2 experience is a full web product.

---

## Monorepo Structure

```
compass/   ← Python CLI package (v1)
api/       ← FastAPI layer (v2)
ui/        ← React + Vite + TypeScript (v2)
```

Both `api/` and `compass/cli.py` call `runner.py`. The clean seam already exists from v1.

---

## Tech Stack

**Frontend:** React + Vite + TypeScript
**Backend:** FastAPI (Python) — standalone API, not a Node BFF

This document's API contract is now the minimal scaffold used to unblock type generation.
Longer-term job orchestration can still evolve on top of the same `runner.py` seam.

---

## Serving

**Development:** Vite dev server on port 5173, FastAPI on port 8000, CORS enabled between them.

**Production:** `vite build` → static files in `ui/dist/` → FastAPI mounts and serves them via `StaticFiles`. One process, one port.

---

## TypeScript Types

Types are generated, not hand-written. No manual sync between Python and TypeScript.

1. FastAPI scaffold completed with Pydantic models
2. FastAPI exposes `/openapi.json` automatically
3. `npx openapi-typescript http://localhost:8000/openapi.json -o ui/src/types/api.ts`
4. All API types derive from the single source of truth

**This is the unblocking dependency for wiring real API calls.** UI components can be built against mock data before this step.

---

## API Endpoints

- `POST /run` — accepts `target_path`, `adapters`, `provider`, `lang`, `reanalyze`; calls `await runner.run(...)`; returns generated output paths
- `GET /output/{adapter}?target_path=...` — returns schema-aligned adapter output for `summary` and `rules`

The scaffold intentionally calls `runner.py` directly. No subprocess, no CLI wrapper.

**Next phase:** a job model in `storage/` plus SSE/WebSocket progress can be layered on later without changing the runner boundary.

---

## Sequencing

```
After v1 adapters done:
  ├── API: FastAPI scaffold + OpenAPI schema       ← ~1 day, unblocks TS type generation
  └── Frontend: UI scaffold + components           ← starts immediately, mock data

  After FastAPI scaffold:
  └── Frontend: generate TS types from OpenAPI     ← replaces manual mock types

  After UI components + TS types:
  └── All: wire frontend to real API
```

---

## What v1 Already Provides

- `runner.py` decoupled from `cli.py` ✅
- `storage/` isolation — job state slots in naturally ✅
- `providers/` abstraction — no changes needed ✅
- Structured JSON outputs (`summary.json`, `analysis_context.json`) — directly servable ✅
- Two-phase design maps cleanly to async job model ✅
