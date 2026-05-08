# Compass Frontend — Contributor Guide
### Issue #61 — Frontend Scaffold

---

## Where we are

Compass v1 CLI is complete. The pipeline runs end-to-end:

```
Collectors (Phase 1) → analysis_context.json → Adapters (Phase 2) → rules.yaml + summary.md + summary.json
```

The frontend (issue #61) is the next active workstream. You don't need the API to start — build against mock data derived from the locked schemas.

**Branch:** `feat/issue-61-frontend-scaffold` off `dev`

**Live design reference:** `docs/Mockups/compass-v5.html` — open in a browser before writing any code.

---

## Stack

**React + Vite + TypeScript.** Pure SPA. No Next.js — FastAPI owns the server layer.

In production, `vite build` produces static files in `ui/dist/` which FastAPI serves directly. One process, one port.

```
compass/   ← Python CLI (v1, done)
api/       ← FastAPI (issue #59, not yet built)
ui/        ← frontend (active)
```

---

## Layout — four columns, always visible

```
[ Nav strip 52px ] [ Section list 216px ] [ Detail 1fr ] [ Rules 280px ]
```

No React Router. No tab toggle. All four panels always mounted.

- **Nav strip** — icon + label buttons: What it does, Start here, Stable, Hotspots, Rules, Config. Active state emerald. Completion tick on visited items.
- **Section list** — user context card at top (name, repo, day), then section headers and item cards. Clicking an item populates the detail and rules panels.
- **Detail panel** — serif typography, breadcrumb, tag pills, body prose, callout boxes, code block, prev/next footer.
- **Rules panel** — contextually filtered rule cards matching the active file. Always visible, never hidden.

**Why not a router or tabs:** Compass has exactly three data surfaces — orientation (summary), conventions (rules), questions (chat). Mounting all three simultaneously means `summary.json` and `rules.yaml` load once at `App` level. All panels share state trivially. Chat always knows what is loaded and what is active. If shareable URLs ever become a requirement, a router can be added — starting with one and retrofitting persistent shared panels is the harder path.

---

## Topbar

Three zones, absolute-positioned:

```
[ Compass wordmark ]     [ Onboarding | Workspace | Community ]     [ settings · avatar · repo pill ]
```

- **Left:** Compass wordmark only. Clean.
- **Centre:** Three product mode tabs — active tab is the primary nav signal.
- **Right:** Light mode toggle, settings icon, avatar, repo/branch pill.

**The three modes:**
- **Onboarding** — structured walkthrough of an unfamiliar codebase (current view)
- **Workspace** — personal notes, saved items, session history
- **Community** — team directory, org chart, Slack invites, notice board

A new hire is not just onboarding with a codebase — they are onboarding with an organisation. These three tabs hold both.

---

## Chat drawer

Collapsible horizontal bar pinned to the bottom. Collapsed: 44px, full viewport width, compass icon as the single tap target. Expands upward to ~52vh.

All four columns remain visible above it at all times — unified space, no breaks.

**Expanded state:** two-panel workspace.
- Left — conversation thread (YOU / COMPASS message labels, conversation bubbles, input)
- Right — output panel (cream body, white header with Output/Diff/Diagram/Canvas tabs, dark code card)

---

## Key interaction: paragraph → rule linking

Paragraphs in the detail panel carry `data-rule` attributes referencing rule IDs. On mouseenter, the corresponding rule card in the rules panel highlights and scrolls into view. On mouseleave, it resets. This is the primary mechanism that makes the connection between content and conventions legible.

---

## Design system

| Token | Value |
|---|---|
| Primary font | Newsreader (serif) — headlines, emphasis |
| UI font | Public Sans — body, labels, UI chrome |
| Code font | JetBrains Mono — code blocks, file paths, rule IDs |
| Accent | Sage emerald `#4A7862` |
| Background | Warm cream `#FDFCFB` |
| Outer shell | `#F0EFED`, max-width 1440px, centered |
| Dark surface | `#1E2329` — code blocks, nav strip active |

**All fonts are self-hosted** in `docs/Mockups/fonts/` — no CDN dependency.

CSS custom properties for everything. Token system is client-themeable from day one:

```css
--color-surface-base       /* page background */
--color-surface-raised     /* cards, panels */
--color-surface-code       /* code blocks */
--color-text-primary
--color-text-secondary
--color-text-muted
--color-accent
--color-border
--font-sans
--font-mono
```

**The reference is Claude.ai, not VS Code.** Compass is a reading environment. Warm neutrals, generous whitespace, typography first. Monospace only where it earns it — file paths, code blocks, rule IDs. Not for everything.

---

## Data shapes — what you're mocking

**`summary.json`**
```typescript
interface SummaryOutput {
  repo_name: string
  generated_at: string          // ISO 8601
  what_it_does: string
  read_first: { path: string; reason: string }[]
  stable:      { path: string; note: string }[]
  hotspots:    { path: string; note: string }[]
  clusters: {
    id: number
    summary: string
    files: string[]
    coupling_pairs: [string, string][]
  }[]
}
```

**`rules.yaml`** (parsed to JSON for the frontend)
```typescript
interface RulesOutput {
  clusters: {
    name: string
    context: string
    golden_file: string
    rules: {
      id: string        // e.g. "DI-01", "HEX-04"
      rule: string
      why: string
      example: string
    }[]
  }[]
}
```

Types will be auto-generated from FastAPI's OpenAPI schema once issue #59 lands. Until then these are hand-written. Don't over-engineer them — they will be replaced.

---

## Open questions

| Question | Status | Impact |
|---|---|---|
| Entry moment | Open | Does the UI open directly into the four-column view, or with a name/role input screen first? Decide with Stuart before building the App entry flow. |
| FastAPI layer (#59) | Not started | Gates real API wiring — not blocking scaffold work |
| TypeScript type generation (#62) | Not started | Blocked on #59 — replaces hand-written interfaces |
| `confidence` field in rules | Schema open | Build the visual component (dots), wire to mock value |
| `gaps` field | Schema open | "No convention found for X" display — same approach |

---

## Key files

| File | Purpose |
|---|---|
| `docs/Mockups/compass-v5.html` | Live interactive prototype — open in browser first |
| `docs/ui-design-iteration-log.md` | Full design decision log, v2 → v5 |
| `docs/frontend-implementation-roadmap.md` | Phase-by-phase build plan |
| `docs/ui-brief-concept-issue-61.md` | Original architecture brief |
| `FRONTEND.md` | v2 FastAPI + frontend architecture spec |
| `ui/` | React + Vite scaffold (to be rebuilt against v5 design) |
| `compass/schemas/summary_schema.py` | Locked schema for `summary.json` |
| `compass/schemas/rules_schema.py` | Locked schema for `rules.yaml` |
| `examples/analysis_context.json` | Real example of pipeline output |

---

## First steps

1. Pull `dev`, checkout `feat/issue-61-frontend-scaffold`
2. Open `docs/Mockups/compass-v5.html` in a browser — read it before touching code
3. Read `docs/frontend-implementation-roadmap.md` for the build sequence
4. Decide the entry moment question with Stuart before writing the App entry flow
5. Set up the token system and base theme first — everything else builds on top of it
