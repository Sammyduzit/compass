# Compass Frontend — Wiring Document
### API integration, state machine, and UI flow

_Read alongside `frontend-implementation-roadmap.md` (component build plan) and `frontend-guide.md` (stack and data shapes)._

---

## API — What's Actually Live

The FastAPI layer (PR #74) plus the async job queue refactor (PR #86, closed #82) are both shipped. `/run` is asynchronous: it returns a job ID immediately, and the frontend polls a status endpoint until the run completes. Build against this contract — there is no synchronous variant to fall back to.

### POST /run

```
POST /run
Body: {
  target_path: string,     // e.g. "/Users/stuart/Projects/my-repo"
  adapters: string[],      // ["rules"] | ["summary"] | ["rules", "summary"] — min 1
  provider: string | null, // "claude" | "codex" | null (uses default)
  lang: string,            // "auto" | "python" | "typescript" — defaults to "auto"
  reanalyze: boolean       // force re-run even if .compass/ cache exists — defaults false
}
Response: { job_id: string }
```

Returns immediately. The run executes in a FastAPI background task on the server. The `job_id` is the handle for everything that follows.

### GET /jobs/{job_id}

```
GET /jobs/{job_id}
Response: {
  job_id: string,
  status: "queued" | "running" | "done" | "failed",
  error: string | null
}
```

Poll every 2 seconds. Stop polling when `status` is `done` or `failed`.

**Status meanings:**
- `queued` — accepted, not yet started
- `running` — collectors and/or adapters in flight
- `done` — outputs written to `.compass/output/`
- `failed` — `error` field carries the message

The API does **not** expose granular sub-steps (e.g. "collecting" vs "synthesizing"). The running phase UI must work from `running` alone — don't design progress chrome that depends on data the backend won't send.

### GET /jobs/{job_id}/output

```
GET /jobs/{job_id}/output
Response: {
  job_id: string,
  output_paths: string[]
}
```

Fetched once `status === 'done'`. Returns the absolute paths Compass just wrote. Useful for display ("written to …") but not strictly required — the frontend can skip straight to `/output/{adapter}` with the `target_path` it already knows.

### GET /output/{adapter}

```
GET /output/summary?target_path={target_path}
GET /output/rules?target_path={target_path}

Response (summary): {
  adapter: "summary",
  output_path: string,
  data: SummaryOutput
}

Response (rules): {
  adapter: "rules",
  output_path: string,
  data: RulesOutput
}
```

Fire both in parallel once the job is `done`. The `data` field is what feeds the panels — unwrap it immediately.

---

## The Four UI Phases

The entire frontend is a single state machine. Every component's render state is driven by which phase is active.

```
empty → input → running → results
              ↑                 |
              └─────────────────┘
                  "New Analysis"
```

| Phase | What the user sees | What triggered it |
|---|---|---|
| `empty` | Four columns, unpopulated. Compass introduces itself. | First load, or after clearing a result |
| `input` | Slide-in panel over the layout. Five fields. | "New Analysis" button tapped |
| `running` | Four columns faded. Chat drawer open, progress shown. | Form submitted |
| `results` | Full v5 layout. All four columns populated. | Run completes, data fetched |

---

## App-Level State Shape

```typescript
type JobStatus = 'queued' | 'running' | 'done' | 'failed'

type AppPhase =
  | { phase: 'empty' }
  | { phase: 'input' }
  | { phase: 'running'; targetPath: string; repoName: string; jobId: string; status: JobStatus }
  | { phase: 'results'; summary: SummaryOutput; rules: RulesOutput; targetPath: string }
```

The `status` field on the running variant is the last value returned by the poll. The UI renders a single indeterminate progress state — the API does not surface sub-steps, so the design does not try to invent them.

Lives at `App` level. `useState` + `useCallback` — no external state library needed.

---

## API Calls & When They Fire

### 1. Submit a run

**Fires when:** User submits the input panel form.

```typescript
const res = await fetch('/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ target_path, adapters, provider, lang, reanalyze })
})
const { job_id } = await res.json()
```

On success: set phase to `running` with the returned `job_id` and `status: 'queued'`. Begin polling immediately.

On error (4xx/5xx): stay on `input` phase, surface the response error below the submit button.

---

### 2. Poll job status

**Fires when:** Phase transitions to `running` — start a `setInterval` at 2-second cadence.

```typescript
const res = await fetch(`/jobs/${jobId}`)
const { status, error } = await res.json()
```

- On every tick: update the running variant's `status`.
- On `done`: clear the interval, advance to step 3.
- On `failed`: clear the interval, transition back to `input` with `error` surfaced.
- On component unmount: clear the interval.

Polling 2s is the recommended cadence — fast enough to feel responsive, slow enough to avoid pummelling the API for runs that take minutes.

---

### 3. Fetch results

**Fires when:** Poll returns `status: 'done'`.

```typescript
const [summaryRes, rulesRes] = await Promise.all([
  fetch(`/output/summary?target_path=${encodeURIComponent(targetPath)}`),
  fetch(`/output/rules?target_path=${encodeURIComponent(targetPath)}`)
])

const summary = (await summaryRes.json()).data
const rules = (await rulesRes.json()).data
```

Wait for both before transitioning to `results`. If either fails, stay on `running` phase and surface a retry option (the job itself succeeded — only the output read failed).

---

## UI State → Component Mapping

### Empty Phase — *hypothesis*

The four-column grid renders fully but unpopulated. The structure is present from the first moment — the user understands what they're about to get before running anything.

**Nav strip:** All six icons visible, none active. No completion ticks.

**Section list:** User context card at top — placeholder name and repo until a run completes. Below it: muted text — "No analysis yet. Run Compass on a repository to get started." No item cards.

**Detail panel:** Centred empty state. Compass wordmark + icon. One line: "Point Compass at a codebase. Get structured onboarding in minutes." Below it: a single primary button — "New Analysis" — which transitions to `input` phase. Nothing else. Generous vertical padding.

**Rules panel:** Three placeholder rule card outlines — ghost borders, no content. Signals where rules will appear without being noisy.

**Chat drawer:** Collapsed bar visible. Tap target present but inactive. Tapping while empty shows: "Run an analysis first to unlock the chat."

**Design note:** The empty state should feel considered, not abandoned. The layout being present frames what is coming.

---

### Input Phase — *hypothesis*

A slide-in panel from the right, overlaying but not replacing the layout. The four columns remain visible at reduced opacity (0.4) — the layout context frames what is about to be populated.

**Slide-in panel:** Fixed width 480px, full height, right-anchored. White background, left hairline border, shadow `0 0 40px rgba(0,0,0,0.12)`.

**Panel header:** "New Analysis" in Newsreader headline. Close icon top-right — returns to `empty` phase.

**Five fields:**

1. **Repository path** — text input. Label: "Repository path". Placeholder: `/path/to/your/repo`. Helper text: "The local path Compass will scan. FastAPI runs locally — no upload needed." Required.

2. **Output** — two checkboxes. Label: "Output". Options: `Rules` and `Summary`, both checked by default. At least one required.

3. **AI provider** — dropdown. Label: "Provider". Options: `Claude` (default), `Codex`.

4. **Language** — dropdown. Label: "Language". Options: `Auto-detect` (default, sends `"auto"`), `Python`, `TypeScript`. Helper text: "Override if Compass picks the wrong language."

5. **Force re-run** — single checkbox, unchecked by default. Label: "Re-analyse from scratch". Helper text: "Ignores any cached results in `.compass/`."

**Submit:** Full-width primary button. Label: "Run Analysis". On submit, fires `POST /run` and transitions to `running` phase.

**Design note:** Five fields does not need a wizard. The slide-in panel handles it — preserves layout context, is dismissible, reads as configuration not navigation.

---

### Running Phase

The slide-in panel closes. The four columns return to full opacity. The chat drawer expands automatically to show progress.

**Left side (chat thread):** A single Compass message — "Running analysis on `{repo_name}`…"

**Right side (output panel):** Header label `PROGRESS`. Body shows the current job status and an elapsed time counter:

```
● Queued        — pending dot, muted
● Running       — emerald dot, pulses while active, becomes a tick on done
```

The two-state model mirrors what `GET /jobs/{job_id}` actually returns. There is no `collecting` / `synthesizing` breakdown to render — the backend does not expose it, and faking client-side stages would lie about progress. If the API ever grows finer-grained states, extend the `JobStatus` type and add rows to the indicator — but only then.

A small "Elapsed: 00:42" counter under the indicator gives the user a sense the system is still alive without claiming more knowledge than we have.

**Four columns during running:** Skeleton loaders — ghost-border placeholder shapes matching the eventual layout. No shimmer. Signals content is incoming without being noisy.

**Failure:** If the poll returns `status: 'failed'`, transition back to `input` phase, pre-fill the form with the previous values, and surface the `error` string above the submit button.

---

### Results Phase

Run complete. Data in state. Chat drawer collapses to 44px bar. Four columns populate.

**Section list:** Repo name in user context card. First section active per nav strip selection.

**Detail panel:** First item in `read_first` selected by default.

**Rules panel:** Rules filtered to the active item.

**Chat drawer:** Collapses. Now active — has full context of both `SummaryOutput` and `RulesOutput`.

**"New Analysis"** — accessible from the topbar right cluster. Transitions back to `input` phase. Current results stay in state until a new run completes.

**`reanalyze` flag:** If the user re-runs the same repo, the `reanalyze` checkbox in the input panel controls whether the cache is busted. Default off — returning to the same repo is instant if `.compass/` already exists.

---

## State Transitions Summary

```
App mounts
  → phase: empty

User taps "New Analysis"
  → phase: input

User submits form
  → POST /run → { job_id }
  → phase: running { jobId, status: 'queued' }

Poll GET /jobs/{job_id} every 2s
  → status: 'queued' → 'running' → 'done'
  → (if 'failed': phase: input with error surfaced)

On status: 'done'
  → Promise.all([GET /output/summary, GET /output/rules])
  → phase: results

User taps "New Analysis" from results
  → phase: input (results preserved until new run completes)
```

---

## Open Questions

| Question | Impact |
|---|---|
| Does the entry moment ask for a name before the empty state? | Affects user context card — name either collected up front or defaulted to system username |
| What is the error UX if the repo path doesn't exist? | Needs inline validation before the API call fires — FastAPI will 422 but that's not a user-friendly message |
| Does the chat work during `running` phase? | No context yet — disable or respond with "Analysis in progress" |
| Is `target_path` stored between sessions? | If yes, returning users could skip directly to results if `.compass/` already exists |
| When does `reanalyze` default to true? | If the user re-opens the input panel after already running the same repo, should it pre-fill with the previous path and default reanalyze to false? |
