# Compass Frontend — Wiring Document
### API integration, state machine, and UI flow

_Read alongside `frontend-implementation-roadmap.md` (component build plan) and `frontend-guide.md` (stack and data shapes)._

---

## API — What's Actually Live

The FastAPI layer merged in PR #74. The actual endpoints differ slightly from Sammy's original description — read these, not the Slack message.

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
Response: { output_paths: string[] }
```

**Current behaviour:** Synchronous. Holds the HTTP connection open for the full run — can be several minutes. Issue #82 will refactor this to a job queue. Build the UI to handle both: the loading state design is valid now; the step-by-step progress design is valid once #82 ships. See the Running Phase section for how to handle both.

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

Fire both in parallel after `/run` completes. The `data` field is what feeds the panels — unwrap it immediately.

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
type AppPhase =
  | { phase: 'empty' }
  | { phase: 'input' }
  | { phase: 'running'; targetPath: string; repoName: string }
  | { phase: 'results'; summary: SummaryOutput; rules: RulesOutput; targetPath: string }
```

**Note:** No `jobId` or `step` in the running state yet — Issue #82 hasn't shipped. When it does, add `jobId: string` and `step: JobStep` to the running variant. The running phase UI is designed to show step progress when available and a simple loading state when not.

Lives at `App` level. `useState` + `useCallback` — no external state library needed.

---

## API Calls & When They Fire

### 1. Submit a run

**Fires when:** User submits the input panel form.

On success: set phase to `running`. When the response resolves, fire the two result fetches simultaneously.

On error: stay on `input` phase, surface error message below the submit button.

**Timeout:** `/run` can take several minutes. Set `fetch` timeout to at least 10 minutes or use `AbortController` with a generous threshold. Do not let the browser default timeout kill a legitimate long run.

---

### 2. Fetch results

**Fires when:** `POST /run` resolves successfully.

```typescript
const [summaryRes, rulesRes] = await Promise.all([
  fetch(`/output/summary?target_path=${encodeURIComponent(targetPath)}`),
  fetch(`/output/rules?target_path=${encodeURIComponent(targetPath)}`)
])

const summary = (await summaryRes.json()).data
const rules = (await rulesRes.json()).data
```

Wait for both before transitioning to `results`. If either fails, stay on `running` phase and surface a retry option.

---

### 3. Job queue polling _(Issue #82 — not yet live)_

Once Issue #82 ships, `/run` will return `{ job_id }` immediately. The running phase will then poll:

```
GET /jobs/{job_id}
Response: {
  status: "queued" | "collecting" | "synthesizing" | "done" | "error",
  step_label: string,
  error?: string
}
```

Poll every 2 seconds via `setInterval`. Clear on unmount and on `done`/`error`. When status reaches `done`, fire the two result fetches. When status is `error`, transition back to `input` with the error surfaced.

**Build the step-progress UI now** — wire it to static state while #82 is pending. Swap in the real poll when it ships.

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

**Current behaviour (synchronous `POST /run`):**

Left side of chat drawer: A single Compass message — "Running analysis on `{repo_name}`…"

Right side (output panel): Header label `PROGRESS`. Body: an animated loading indicator and elapsed time counter. No step breakdown yet — the API doesn't provide it.

**Future behaviour (after Issue #82 — job queue):**

Right side (output panel): Four step indicators stacked vertically.

```
● Queued
● Collecting        ← active step pulses
● Synthesizing
● Done
```

Active step: emerald dot, primary text. Below it: `step_label` from the poll response — e.g. "Scanning import graph…". Completed steps: tick, muted text. Pending steps: ghost dot, faint text.

**Build the step UI now against static/mock state.** It costs nothing to build it correctly — swap in real poll data when #82 ships.

**Four columns during running:** Skeleton loaders — ghost-border placeholder shapes matching the eventual layout. No shimmer. Signals content is incoming without being noisy.

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
  → POST /run (synchronous — awaits full completion)
  → phase: running

POST /run resolves
  → Promise.all([GET /output/summary, GET /output/rules])
  → phase: results

─── After Issue #82 ships ───────────────────────────────

User submits form
  → POST /run returns { job_id } immediately
  → phase: running
  → poll GET /jobs/{job_id} every 2s
  → step updates: queued → collecting → synthesizing → done
  → Promise.all([GET /output/summary, GET /output/rules])
  → phase: results

─────────────────────────────────────────────────────────

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
