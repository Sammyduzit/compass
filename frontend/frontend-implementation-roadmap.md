# Compass Frontend — Implementation Roadmap
### From v5 mockup to working React app

_Reference: `frontend/mockups/compass-v5.html` — open this before reading._

---

## Overview

This document breaks the v5 mockup into a concrete, sequenced build plan. Each phase produces something visible and testable before the next begins. Phases 1–8 are buildable right now against mock data. Phase 9 (API integration) can land any time after Phase 8 — the FastAPI layer is live (issue #59).

---

## Phase 0 — Foundation (do this first, everything depends on it)

**Goal:** Token system, fonts, TypeScript interfaces, and mock data files in place before any component is written.

### 0.1 CSS token system
Create `ui/src/styles/tokens.css`. Every value in the design must be a token — no hardcoded hex or px values anywhere in component styles.

```css
:root {
  /* Surfaces */
  --color-surface-outer: #F0EFED;
  --color-surface-base: #FDFCFB;
  --color-surface-raised: #FFFFFF;
  --color-surface-code: #1E2329;

  /* Text */
  --color-text-primary: #1A1A1A;
  --color-text-secondary: #4A4A4A;
  --color-text-muted: #9A9A9A;

  /* Accent */
  --color-accent: #4A7862;
  --color-accent-light: #EBF2EE;

  /* Borders */
  --color-border: rgba(0, 0, 0, 0.08);
  --color-border-strong: rgba(0, 0, 0, 0.15);

  /* Fonts */
  --font-serif: 'Newsreader', Georgia, serif;
  --font-sans: 'Public Sans', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Layout */
  --shell-max-width: 1440px;
  --nav-strip-width: 52px;
  --section-list-width: 216px;
  --rules-panel-width: 280px;
  --topbar-height: 48px;
  --chat-collapsed-height: 44px;
  --chat-expanded-height: 52vh;
}
```

### 0.2 Font loading
Fonts are self-hosted in `frontend/fonts/`. Copy the woff2 files and `fonts.css` into `ui/src/styles/fonts/` and import at the root. No CDN.

### 0.3 TypeScript interfaces
Create `ui/src/types.ts` with `SummaryOutput` and `RulesOutput` interfaces (see `frontend/frontend-guide.md` for the shapes). These are hand-written until issue #62 lands.

### 0.4 Mock data
Create `ui/src/mock/summary.json` and `ui/src/mock/rules.json` using real-looking Compass output. Base them on `examples/analysis_context.json`. The mock data drives every panel until API integration.

---

## Phase 1 — Shell & Topbar

**Goal:** The outer chrome is in place. Nothing inside it yet.

### 1.1 Root shell
`App.tsx` renders a full-viewport layout:
- Outer background: `--color-surface-outer`
- Inner shell: max-width `--shell-max-width`, centered, `--color-surface-base`, min-height 100vh

### 1.2 Topbar component — `Topbar.tsx`
Three zones via CSS grid or flexbox:

**Left:** Compass wordmark (Newsreader, ~18px, `--color-text-primary`).

**Centre (absolute):** Three tab buttons — `Onboarding | Workspace | Community`. Active tab has an underline or subtle pill in `--color-accent`. Inactive tabs are `--color-text-muted`. Tab state lives in `App`-level `useState`.

**Right:** Light mode toggle icon, settings icon, avatar circle, repo/branch pill (`service-api · main`).

Height: `--topbar-height`. Border-bottom: `--color-border`.

### 1.3 Tab state
Only `Onboarding` renders the four-column layout. `Workspace` and `Community` can render placeholder panels for now — they are out of scope for this phase.

---

## Phase 2 — Four-Column Grid

**Goal:** The four columns exist with correct widths and scroll behaviour. No content yet.

### 2.1 Layout component — `WorkspaceLayout.tsx`
CSS grid:
```css
grid-template-columns: var(--nav-strip-width) var(--section-list-width) 1fr var(--rules-panel-width);
height: calc(100vh - var(--topbar-height) - var(--chat-collapsed-height));
overflow: hidden;
```

Each column is `overflow-y: auto` independently — they scroll separately.

### 2.2 Column stubs
Four placeholder components: `NavStrip`, `SectionList`, `DetailPanel`, `RulesPanel`. Each renders a coloured background and its name so you can see the grid is correct before filling them.

---

## Phase 3 — Nav Strip

**Goal:** `NavStrip` is interactive. Clicking a section updates the active section in shared state.

### 3.1 Nav strip component — `NavStrip.tsx`
Width: `--nav-strip-width` (52px). Background: white. Right border: `--color-border`.

Six icon-button items, stacked vertically:
- What it does
- Start here
- Stable
- Hotspots
- Rules
- _(divider)_
- Config (bottom, settings icon)

Each item: icon (24px) + label below (9px, mono, uppercase). Active state: emerald left-border (3px) + `--color-accent` icon tint. Visited items show a small tick overlay on the icon.

Active section state lives in `App` (or a context). `NavStrip` receives `activeSection` and `onSectionChange` as props.

### 3.2 Light mode toggle
A sun/moon icon button at the bottom of the strip (above Config). Toggles a `data-theme` attribute on `<html>`. Dark mode tokens are a Phase 7 concern — just wire the toggle now.

---

## Phase 4 — Section List Panel

**Goal:** `SectionList` shows the user context card and the item list for the active section.

### 4.1 User context card
At the top of the panel, above all section content:
- Avatar initial circle (`--color-accent` bg)
- Name + role (or just name if role is not yet collected)
- Repo name + day number ("Day 1")

This is the only place user identity appears. Not the topbar.

### 4.2 Section content
Below the context card, render items for the active section. Each section maps to a field in `summary.json`:

| Section | Data source |
|---|---|
| What it does | `what_it_does` (prose — render as a single card) |
| Start here | `read_first[]` |
| Stable | `stable[]` |
| Hotspots | `hotspots[]` |
| Rules | `clusters[]` |

### 4.3 Item cards
Each item in the list is a card:
- File name (no `src/` prefix in the label)
- One-line note below
- Compass icon button top-right (opens chat with this item's context)
- Active state: `--color-accent` left border (3px)

Clicking a card sets `activeItem` in shared state, which drives the detail and rules panels.

---

## Phase 5 — Detail Panel

**Goal:** `DetailPanel` renders the full content for the selected item.

### 5.1 Panel structure
Inner wrapper with `width: calc(100% - 116px); margin: 0 auto` — gives equal 58px padding on both sides regardless of viewport width. (Do not use padding % — it resolves against the parent container, not the column.)

### 5.2 Breadcrumb
Small row above the headline: `Section › filename`. Each segment is `cursor: pointer` with a hover underline.

### 5.3 Tag pills
Below the breadcrumb. Pills like `ENTRY POINT`, `INVERSION OF CONTROL`. Rounded, border in `--color-border`, small mono text. All pills are `cursor: pointer` with hover state — they imply navigation even if the target is a future concern.

### 5.4 Headline
Newsreader, ~32px, with italic on the key phrase. This is the strongest typographic moment — give it room above and below.

### 5.5 Body prose
Public Sans, ~15px, line-height ~1.7. Each paragraph that references a rule carries a `data-rule` attribute:
```html
<p data-rule="DI-01">...</p>
```

### 5.6 "Why this matters" callout
A tinted box (`--color-accent-light`, left border in `--color-accent`). Label: `WHY THIS MATTERS` in small caps mono. Body prose inside.

### 5.7 Code block
Dark card (`--color-surface-code`, border-radius 6px). Header: filename left, language badge right. Body: JetBrains Mono, 13px, syntax highlighted. Use a lightweight highlighter (Shiki or Prism) — do not hand-roll this.

### 5.8 Prev/next footer
Small row at the bottom: `← Previous file` and `Next file →` links. Muted text, hover underline.

---

## Phase 6 — Rules Panel

**Goal:** `RulesPanel` renders rule cards filtered to the active item.

### 6.1 Rule cards
Each card:
- ID badge top-left (`DI-01`, `HEX-04`) — small, `--color-accent` bg, white text, mono
- Rule statement — body text, ~14px
- "Why" line — muted, smaller
- Optionally: example code (collapsed, expand on click)
- "Golden file" label if applicable — small pill

### 6.2 Highlight state
Each card accepts an `isHighlighted` prop. When highlighted (from paragraph hover in the detail panel): elevated shadow, `--color-accent-light` background, smooth transition.

### 6.3 Footer
"View all N rules" link at the bottom of the panel. Out of scope for this phase — render it as static text for now.

---

## Phase 7 — Paragraph → Rule Linking

**Goal:** Hovering a paragraph in the detail panel highlights and scrolls the corresponding rule card.

### 7.1 Event wiring
In `DetailPanel`, attach `onMouseEnter` and `onMouseLeave` handlers to every element with a `data-rule` attribute. On enter, call `onRuleHighlight(ruleId)` (prop or context). On leave, call `onRuleHighlight(null)`.

### 7.2 Rule panel receiving
`RulesPanel` receives `highlightedRuleId`. Each rule card checks if its ID matches and applies the highlight class. On highlight, scroll the card into view (`scrollIntoView({ behavior: 'smooth', block: 'nearest' })`).

---

## Phase 8 — Chat Drawer

**Goal:** Chat drawer is interactive — collapses, expands, and accepts input.

### 8.1 Collapsed state
Full viewport width (breaks out of the `--shell-max-width` constraint using negative margins or a separate stacking context). Height: `--chat-collapsed-height` (44px). Background white, top border `--color-border`.

Centre: Compass logo icon button as the single tap target. Clicking expands the drawer.

Right end: Reserved space for "add to workspace" function (render as empty for now).

### 8.2 Expanded state
Animates upward to `--chat-expanded-height` (52vh). Two-panel workspace inside:

**Left — conversation thread (1fr):**
- Scrollable message list
- Messages labelled `YOU` and `COMPASS` (small caps mono, muted)
- User messages: right-aligned, white bg, border
- Compass messages: left-aligned, `--color-surface-outer` bg
- Input bar at the bottom: text field + send button, `⌘K` hint

**Right — output panel (1fr):**
- Background: `--color-surface-base`
- Header (white, border-bottom): `OUTPUT` label left (mono, muted) + tab row right (`Diff | Diagram | Canvas`) + share icon
- Body: 12px padding, contains a dark code card (`--color-surface-code`, border-radius 6px)
- Code card header: filename left + diff badge (`+8 / −3`) right

### 8.3 Chat context
When a user clicks the compass icon on an item card, open the drawer and pre-populate the input with that item's context. The chat always knows `activeSection` and `activeItem`.

---

## Phase 9 — API Integration

**Goal:** Replace mock data with live FastAPI responses.

The FastAPI layer is live (issue #59, PRs #74 + #86). The full async contract is in `frontend-wiring.md` — implement it there, not here. The short version:

- `POST /run` → `{ job_id }` (kicks off a background run)
- `GET /jobs/{job_id}` → poll for `status: 'queued' | 'running' | 'done' | 'failed'`
- `GET /output/summary?target_path={path}` → `{ adapter, output_path, data: SummaryOutput }`
- `GET /output/rules?target_path={path}` → `{ adapter, output_path, data: RulesOutput }`

There is no `/chat` endpoint yet. The chat drawer's API contract is an open question — leave the input wired to a no-op handler until the design is decided.

TypeScript interfaces will be auto-generated from the OpenAPI schema (issue #62, still open) and replace the hand-written ones from Phase 0.

---

## Component tree (reference)

```
App
├── Topbar
│   ├── Wordmark
│   ├── TabNav (Onboarding | Workspace | Community)
│   └── TopbarRight (toggle, settings, avatar, repo pill)
├── WorkspaceLayout                    ← four-column grid
│   ├── NavStrip
│   ├── SectionList
│   │   ├── UserContextCard
│   │   └── ItemCard[]
│   ├── DetailPanel
│   │   ├── Breadcrumb
│   │   ├── TagPills
│   │   ├── Headline
│   │   ├── BodyProse (with data-rule attrs)
│   │   ├── WhyCallout
│   │   ├── CodeBlock
│   │   └── PrevNextFooter
│   └── RulesPanel
│       └── RuleCard[] (with highlight state)
└── ChatDrawer
    ├── CollapsedBar
    └── ExpandedWorkspace
        ├── ChatThread
        │   ├── MessageList
        │   └── ChatInput
        └── OutputPanel
            ├── OutputHeader (tabs)
            └── OutputCodeCard
```

---

## Build sequence summary

| Phase | Deliverable | Blocked on |
|---|---|---|
| 0 | Tokens, fonts, types, mock data | Nothing |
| 1 | Shell + Topbar | Phase 0 |
| 2 | Four-column grid skeleton | Phase 1 |
| 3 | Nav strip (interactive) | Phase 2 |
| 4 | Section list panel | Phase 3 |
| 5 | Detail panel content | Phase 4 |
| 6 | Rules panel | Phase 4 |
| 7 | Paragraph → rule linking | Phases 5 + 6 |
| 8 | Chat drawer | Phase 2 |
| 9 | API integration | Phases 4–8 (FastAPI is live) |

Phases 3, 4, 5, 6, and 8 can proceed in parallel once Phase 2 is done.
