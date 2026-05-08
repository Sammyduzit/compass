# Compass Frontend — Wiring Document
### API integration, state machine, and UI flow

_Read alongside `frontend-implementation-roadmap.md` (component build plan) and `frontend-guide.md` (stack and data shapes)._

---

## The Four UI Phases

The entire frontend is a single state machine with four phases. Every component's render state is driven by which phase is active.

```
empty → input → running → results
              ↑                 |
              └─────────────────┘
                  "New Analysis"
```

| Phase | What the user sees | What triggered it |
|---|---|---|
| `empty` | Four columns, unpopulated. Compass introduces itself. | First load, or after clearing a result |
| `input` | Slide-in panel over the layout. Three fields. | "New Analysis" button tapped |
| `running` | Four columns faded slightly. Chat drawer open, progress in output panel. | Form submitted |
| `results` | Full v5 layout. All four columns populated. | Job reaches `done`, data fetched |

---

## App-Level State Shape

```typescript
type AppPhase =
  | { phase: 'empty' }
  | { phase: 'input' }
  | { phase: 'running'; jobId: string; step: JobStep; targetPath: string }
  | { phase: 'results'; summary: SummaryOutput; rules: RulesOutput; targetPath: string }

type JobStep = 'queued' | 'collecting' | 'synthesizing' | 'done'
```

Lives at `App` level. All panels receive the relevant slice as props. No external state library needed — `useState` + `useCallback` at `App` is sufficient until the API layer proves otherwise.

---

## API Calls & When They Fire

### 1. Submit a run

**Fires when:** User submits the input panel form.

```
POST /run
Body: {
  target_path: string,   // e.g. "/Users/stuart/Projects/my-repo"
  adapters: string[],    // ["rules"] | ["summary"] | ["rules", "summary"]
  provider: string       // "claude" | "codex"
}
Response: { job_id: string }
```

On success: store `job_id`, set phase to `running`, begin polling.

On error: stay on `input` phase, surface error message below the submit button.

---

### 2. Poll for job status

**Fires when:** Phase is `running`. Poll every 2 seconds.

```
GET /jobs/{job_id}
Response: {
  status: "queued" | "collecting" | "synthesizing" | "done" | "error",
  step_label: string,    // human-readable: "Scanning imports…", "Building rules…"
  error?: string
}
```

Update `step` in state on each poll response. When `status === "done"`, stop polling and fire the two result fetches simultaneously. When `status === "error"`, transition back to `input` phase with the error surfaced.

**Polling strategy:** `setInterval` at 2000ms. Clear on unmount and on `done`/`error`. Do not retry on network error — surface a "lost connection" message and offer a manual retry.

---

### 3. Fetch results

**Fires when:** Job status reaches `done`. Both requests fire in parallel.

```
GET /output/summary?target_path={target_path}
Response: SummaryOutput (see frontend-guide.md for shape)

GET /output/rules?target_path={target_path}
Response: RulesOutput (see frontend-guide.md for shape)
```

`Promise.all([fetchSummary, fetchRules])` — wait for both before transitioning to `results`. If either fails, surface an error and stay on `running` phase with a retry option.

On success: transition to `results` phase, pass both payloads into App state.

---

## UI State → Component Mapping

### Empty Phase — *hypothesis*

The four-column grid renders but unpopulated. The layout structure is fully present — the user can orient themselves before any data exists.

**Nav strip:** All six icons visible, none active. No completion ticks.

**Section list:** User context card at top (name and repo pulled from local state if previously set, otherwise placeholder). Below it: a single centred prompt — "No analysis yet. Run Compass on a repository to get started." Muted text, no cards.

**Detail panel:** Centred empty state. Compass wordmark + icon at centre. One line of description: "Point Compass at a codebase. Get structured onboarding in minutes." Below it: a single primary button — "New Analysis" — which transitions to `input` phase. Generous vertical padding above and below. Nothing else.

**Rules panel:** Three placeholder rule card outlines — ghost borders, no content, subtle shimmer or just static empty state. Signals that this is where rules will appear without being noisy.

**Chat drawer:** Collapsed bar visible. Compass icon tap target present but chat is inactive until results exist — tapping it in empty phase could show a message: "Run an analysis first to unlock the chat."

**Design note:** The empty state should feel considered, not abandoned. The four-column structure being present from the start means the user understands what they're about to get before they've run anything.

---

### Input Phase — *hypothesis*

A slide-in panel appears from the right, overlaying — but not replacing — the existing layout. The four columns remain visible beneath it at reduced opacity (0.4). The layout context stays in view because it frames what is about to be populated.

**Slide-in panel dimensions:** Fixed width ~480px, full height, right-anchored. Background `{colors.surface-raised}` (white), left border `{colors.hairline}`, shadow `0 0 40px rgba(0,0,0,0.12)`.

**Panel header:** "New Analysis" in `{typography.headline-md}` (Newsreader). Close icon top-right returns to `empty` phase.

**Three fields:**

1. **Repository path** — labelled text input. Label: "Repository path". Placeholder: `/path/to/your/repo`. Full width. Validation: non-empty on submit. Helper text: "The local path Compass will scan. FastAPI runs locally — no upload needed."

2. **Adapters** — two checkboxes. Label: "Output". Options: `Rules` (checked by default) and `Summary` (checked by default). At least one must be selected on submit.

3. **Provider** — dropdown. Label: "AI provider". Options: `Claude` (default), `Codex`. Single select.

**Submit:** Full-width primary button at the bottom. Label: "Run Analysis". Fires `POST /run`, transitions to `running` phase.

**Design note:** Three fields does not need a wizard. It does not need steps. The slide-in panel is the right pattern — it preserves the layout context, it's dismissible, and it communicates that this is a configuration action, not a new page.

---

### Running Phase

The slide-in panel closes. The four columns return to full opacity. The chat drawer expands automatically to show progress in the output panel.

**Left side of chat drawer (thread):** A single Compass message: "Running analysis on `{repo_name}`…" — updates as steps progress.

**Right side of chat drawer (output panel):** This is where the job progress lives.

Output panel header: `PROGRESS` label left, no tabs yet (tabs appear in results phase).

Output panel body: Four step indicators stacked vertically.

```
● Queued          ← active step pulses, completed steps get a tick
● Collecting
● Synthesizing
● Done
```

Each step shows its `step_label` from the poll response below the step name — e.g. "Scanning import graph…", "Running ast-grep patterns…", "Building rules from context…". This is the real-time feedback Sammy referenced.

Active step: emerald dot, `{colors.primary}` text. Completed step: tick icon, `{colors.muted}` text. Pending step: ghost dot, `{colors.faint}` text.

**Four columns during running:** Section list, detail panel, and rules panel show skeleton loaders matching their eventual layout — placeholder card shapes, no shimmer needed, just ghost borders at reduced opacity. Signals that content is incoming without being noisy.

---

### Results Phase

Job is done. Data is in state. The chat drawer collapses back to its 44px bar. The four columns populate.

**Section list:** Populated with the active section's items from `SummaryOutput`. User context card shows the repo name and "Just now" or the generation timestamp.

**Detail panel:** First item in "Start here" (`read_first[0]`) selected by default. Full detail content rendered.

**Rules panel:** Rules filtered to the active item.

**Chat drawer:** Collapses. Now active — chat has full context of both `SummaryOutput` and `RulesOutput`. "New Analysis" is accessible via a small button in the topbar right cluster (next to settings and avatar) to return to `input` phase without losing the current results until the new run completes.

---

## State Transitions Summary

```
App mounts
  → phase: empty

User taps "New Analysis"
  → phase: input

User submits form
  → POST /run
  → phase: running (jobId, step: 'queued')

Poll GET /jobs/{id} every 2s
  → step updates: queued → collecting → synthesizing → done

Step reaches 'done'
  → Promise.all([GET /output/summary, GET /output/rules])
  → phase: results (summary, rules, targetPath)

User taps "New Analysis" from results
  → phase: input (results preserved in state until new run completes)
```

---

## Open Questions

| Question | Impact |
|---|---|
| Does the entry moment ask for a name before showing the empty state? | Affects user context card in section list — name is either collected or defaulted to system username |
| What is the error UX if the repo path doesn't exist or is inaccessible? | Needs inline validation in the input panel before the API call fires |
| Does the chat work during the `running` phase? | If the LLM has no context yet, chat is either disabled or responds with "Analysis in progress" |
| Is `target_path` stored between sessions? | If yes, returning users skip directly to results phase on load if a previous result exists |
| What triggers a re-run vs viewing an existing result? | Need to clarify whether results are persisted in `.compass/` and loadable without re-running |
