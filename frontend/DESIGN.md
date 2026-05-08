# Design System: Compass

## Overview

Compass is a developer onboarding tool. The interface is a **four-column reading environment** — not a dashboard, not a terminal, not a productivity app. The atmosphere is calm and editorial: a warm cream canvas, generous whitespace, and serif headlines that give content authority before a word is read.

The base surface is **warm cream** (`{colors.canvas}` — #FDFCFB) sitting inside an **outer shell** (`{colors.shell}` — #F0EFED) that frames the max-width container. The distinction between canvas and shell is subtle but essential — it grounds the four-column layout without borders or shadows doing the heavy lifting.

The single accent is **sage emerald** (`{colors.primary}` — #4A7862) — muted, natural, never electric. It appears on active nav states, rule ID badges, and primary actions only. The dark surface (`{colors.surface-dark}` — #1E2329) is reserved exclusively for code blocks and never bleeds into the surrounding UI.

**Key Characteristics:**
- Warm cream canvas (`{colors.canvas}` — #FDFCFB) inside a slightly darker shell (`{colors.shell}` — #F0EFED). The shell is the page; the canvas is the product.
- Sage emerald primary (`{colors.primary}` — #4A7862). Used sparingly — active states, rule ID badges, left-border active indicators. Never as a background fill on large surfaces.
- Newsreader serif for all headlines and the wordmark. Public Sans for all UI chrome and body prose. JetBrains Mono only for rule IDs, file paths, and code blocks.
- Dark code surface (`{colors.surface-dark}` — #1E2329) isolated to code blocks. The surrounding UI never goes dark.
- Four columns always visible — no modals, no routing, no tab switching. The layout is the product.
- Border radius is restrained: 6px for cards and pills, 8px for code blocks. Nothing rounder.
- Borders are ghost-weight: `rgba(0,0,0,0.07)`. Structural lines, never decorative.

---

## Colors

### Brand & Accent
- **Sage Emerald / Primary** (`{colors.primary}` — #4A7862): The single accent. Active nav indicators, rule ID badges, left-border active states on item cards, primary action buttons. Muted and natural — not a tech green, not neon.
- **Emerald Dim** (`{colors.primary-dim}` — #3A6252): Pressed / hover-darker variant of the primary.
- **Emerald Pale** (`{colors.primary-pale}` — #EBF3EE): Tinted background for callout boxes, highlighted rule cards, active tag pills. The accent's lightest wash.

### Surface
- **Shell** (`{colors.shell}` — #F0EFED): The outer page background, visible beyond the max-width container. Slightly darker than canvas — frames the product without a border.
- **Canvas** (`{colors.canvas}` — #FDFCFB): The primary product surface. Warm cream — the column backgrounds, the default reading surface.
- **Surface Raised** (`{colors.surface-raised}` — #FFFFFF): White. Reserved for cards, the topbar, the chat drawer collapsed bar. Never used as a page background.
- **Surface Dark** (`{colors.surface-dark}` — #1E2329): Deep slate. Code blocks only. The contrast against cream is intentional — ink on paper.
- **Surface Dark Mid** (`{colors.surface-dark-mid}` — #2D3741): Elevated surfaces inside dark code cards — code block headers, line number gutters.
- **Hairline** (`{colors.hairline}` — rgba(0,0,0,0.07)): All structural borders. Used at 1px everywhere. Ghost-weight — the layout breathes.
- **Hairline Ghost** (`{colors.hairline-ghost}` — rgba(0,0,0,0.05)): Even softer. Card drop shadows, inner dividers within panels.

### Text
- **Ink** (`{colors.ink}` — #1A1C1B): All headlines and primary text. Warm dark, not pure black.
- **Body** (`{colors.body}` — #3A3D3B): Default running prose in the detail panel.
- **Muted** (`{colors.muted}` — #717975): Secondary labels, breadcrumb segments, file notes, nav labels.
- **Faint** (`{colors.faint}` — #A0A8A4): Captions, timestamps, separator characters, placeholder text.
- **On Primary** (`{colors.on-primary}` — #FFFFFF): Text on emerald-fill surfaces.
- **On Dark** (`{colors.on-dark}` — #E8ECE9): Body text inside dark code surfaces. Slightly warm white.
- **On Dark Muted** (`{colors.on-dark-muted}` — #8A9490): Secondary labels inside code blocks — line numbers, comments, language badges.

### Semantic
- **Success** (`{colors.success}` — #4A7862): Reuses primary. Completion ticks on nav items.
- **Error** (`{colors.error}` — #BA1A1A): Validation errors only.

---

## Typography

### Font Family
**Newsreader** (serif) carries all headlines, the wordmark, and the editorial callout body. **Public Sans** (humanist sans) carries all UI chrome, navigation, body prose, and labels. **JetBrains Mono** handles rule IDs, file paths, tag pill labels, and all code blocks.

Newsreader is a screen-optimised optical serif — not a legacy print face. It reads with authority at 36px and remains legible at 14px italic. Public Sans is neutral and functional without being cold. JetBrains Mono is the only monospace — it appears sparingly, which is what gives it signal.

### Hierarchy

| Token | Size | Weight | Line Height | Letter Spacing | Font | Use |
|---|---|---|---|---|---|---|
| `{typography.display}` | 36px | 600 | 1.18 | -0.02em | Newsreader | Main detail panel headline |
| `{typography.headline-lg}` | 24px | 600 | 1.25 | -0.01em | Newsreader | Section headings |
| `{typography.headline-md}` | 18px | 600 | 1.3 | -0.01em | Newsreader | Card titles, panel sub-heads |
| `{typography.wordmark}` | 17px | 600 | 1.0 | -0.01em | Newsreader | Topbar wordmark only |
| `{typography.callout-italic}` | 14.5px | 400 italic | 1.65 | 0 | Newsreader | "Why this matters" callout body |
| `{typography.body-lg}` | 15px | 400 | 1.65 | 0 | Public Sans | Detail panel prose |
| `{typography.body-md}` | 14px | 400 | 1.6 | 0 | Public Sans | Default running text |
| `{typography.label-md}` | 13px | 500 | 1.4 | 0 | Public Sans | Nav tabs, item card titles, button labels |
| `{typography.label-sm}` | 12px | 400 | 1.4 | 0 | Public Sans | Secondary labels, metadata |
| `{typography.mono-body}` | 11px | 500 | 1.6 | 0 | JetBrains Mono | Code block body text |
| `{typography.mono-label}` | 9.5px | 700 | 1.2 | 0.1em | JetBrains Mono | Rule IDs, tag pills, callout section labels |
| `{typography.code}` | 13px | 400 | 1.6 | 0 | JetBrains Mono | Code displayed in detail panel |

### Principles
Display and headline weights are 600 — heavier than Claude.ai's editorial 400, because Compass is a product interface, not a marketing page. Negative letter-spacing on Newsreader headlines is non-negotiable. JetBrains Mono at 9.5px / 700 / 0.1em tracking for rule IDs gives them a badge quality — distinct, official, readable at a glance. Public Sans body never exceeds weight 500.

---

## Layout

### Shell & Container
- **Max content width:** 1440px, centered. The outer shell (#F0EFED) fills the viewport beyond this.
- **Column grid:** Four fixed columns inside the shell — `52px nav strip | 216px section list | 1fr detail | 280px rules panel`.
- **Topbar:** 48px, always visible, sits above the four columns.
- **Chat drawer:** Pinned to the bottom, full viewport width. Collapsed at 44px. Expands upward to 52vh without disturbing the columns above.
- **Scrolling:** Each column scrolls independently. The shell never scrolls.

### Spacing System
- **Base unit:** 4px.
- **Tokens:** `{spacing.xs}` 8px · `{spacing.sm}` 16px · `{spacing.md}` 24px · `{spacing.lg}` 32px · `{spacing.xl}` 48px.
- **Detail panel content padding:** 58px left and right, achieved via inner wrapper `width: calc(100% - 116px); margin: 0 auto`. Never via percentage padding — percentage resolves against the parent container, not the column.
- **Card internal padding:** 12px for item cards in the section list, 16px for rule cards in the rules panel.

### Whitespace Philosophy
Content is the loudest thing on screen. Whitespace does the hierarchy work — not colour, not weight alone. The cream surfaces and ghost borders mean the layout has almost no visual noise. A developer opening Compass sees the headline before anything else.

---

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Column backgrounds, outer shell |
| Hairline | 1px `{colors.hairline}` | Column dividers, topbar bottom, card edges |
| Card | `{colors.surface-raised}` bg + `0 2px 12px rgba(0,0,0,0.04), 0 0 0 1px {colors.hairline-ghost}` | Item cards, rule cards |
| Dark surface | `{colors.surface-dark}` bg | Code blocks — isolated, not floating |
| Highlight | `{colors.primary-pale}` bg + elevated card shadow | Rule card hover/linked state |

Depth is communicated through surface colour, not shadow. The only meaningful shadow is on cards — and it is deliberately faint. The dark code surface has its own internal depth (syntax colouring, header row) which makes external shadows redundant.

---

## Shapes

| Token | Value | Use |
|---|---|---|
| `{rounded.pill}` | 4px | Tag pills, rule ID badges |
| `{rounded.card}` | 6px | Item cards, rule cards |
| `{rounded.code}` | 8px | Code blocks |
| `{rounded.full}` | 9999px | Avatar circles, icon buttons |

Nothing exceeds 8px. The interface is structured and rectilinear — generous rounding would undercut the editorial authority.

---

## Components

### Topbar
**`topbar`** — 48px fixed header. `{colors.surface-raised}` background, 1px `{colors.hairline}` bottom border. Three zones:
- **Left:** Compass wordmark in `{typography.wordmark}` (Newsreader 17px / 600). A small 22×22px emerald square icon precedes it.
- **Centre (absolute positioned):** Three tab buttons — Onboarding | Workspace | Community. Active tab: `{colors.primary-pale}` background, `{colors.primary}` text, weight 600. Inactive: `{colors.muted}` text, weight 500.
- **Right:** Light mode toggle icon, settings icon, avatar circle (28px), repo/branch pill.

### Nav Strip
**`nav-strip`** — 52px wide left column. `{colors.surface-raised}` background, 1px `{colors.hairline}` right border. Six icon-button items stacked vertically: What it does, Start here, Stable, Hotspots, Rules, Config (bottom). Each item: 24px icon + 9px mono label below. Active state: 3px `{colors.primary}` left border + emerald icon tint. Visited items carry a small completion tick overlay on the icon.

### Section List Panel
**`section-list`** — 216px wide. `{colors.canvas}` background, 1px `{colors.hairline}` right border. User context card at top (avatar initial circle in `{colors.primary}`, name, repo, day number). Section headers and item cards below.

**`item-card`** — `{colors.surface-raised}` background, `{rounded.card}` (6px), card shadow. File name in `{typography.label-md}`, one-line note in `{typography.label-sm}` / `{colors.muted}`. Compass icon button top-right — opens chat with this item's context. Active state: 3px `{colors.primary}` left border.

### Detail Panel
**`detail-panel`** — Flex 1fr. `{colors.canvas}` background. Inner content wrapper at `calc(100% - 116px)` centered.

**`breadcrumb`** — Small row above headline. `{typography.label-sm}` / `{colors.muted}`. Each segment `cursor: pointer` with hover underline. Separator in `{colors.faint}`.

**`tag-pill`** — Below breadcrumb. `{rounded.pill}` (4px), 1px `{colors.hairline}` border, `{typography.mono-label}` (JetBrains Mono 9.5px / 700 / 0.1em), `cursor: pointer`. Text in `{colors.muted}`.

**`main-headline`** — `{typography.display}` (Newsreader 36px / 600 / -0.02em). Italic `<em>` on the key phrase. Generous top margin — this is the loudest element on screen.

**`body-prose`** — `{typography.body-lg}` / `{colors.body}`. Paragraphs carry `data-rule` attributes linking to rule IDs. On hover, the corresponding rule card in the rules panel highlights and scrolls into view.

**`callout-box`** — `{colors.primary-pale}` background, 3px `{colors.primary}` left border, `{rounded.card}` (6px). Label row: `{typography.mono-label}` / `{colors.primary}` ("WHY THIS MATTERS"). Body in `{typography.callout-italic}` (Newsreader italic).

**`code-block`** — `{colors.surface-dark}` background, `{rounded.code}` (8px). Header row: filename left in `{typography.mono-body}` / `{colors.on-dark-muted}`, language badge right. Body: `{typography.code}` (JetBrains Mono 13px), syntax highlighted. Sits as a contained card — never full-width bleeds into surrounding cream.

**`prev-next-footer`** — Small row at panel bottom. `← Previous` and `Next →` in `{typography.label-sm}` / `{colors.muted}`. Hover underline.

### Rules Panel
**`rules-panel`** — 280px wide. `{colors.canvas}` background, 1px `{colors.hairline}` left border.

**`rule-card`** — `{colors.surface-raised}` background, `{rounded.card}` (6px), card shadow. ID badge top-left: `{colors.primary}` fill, `{colors.on-primary}` text, `{typography.mono-label}`, `{rounded.pill}` (4px). Rule statement in `{typography.body-md}`. Why line in `{typography.label-sm}` / `{colors.muted}`. Highlighted state (triggered by paragraph hover in detail panel): `{colors.primary-pale}` background, elevated shadow, smooth transition.

**`golden-file-label`** — Small pill on qualifying rule cards. `{colors.primary-pale}` background, `{colors.primary}` text.

### Chat Drawer
**`chat-drawer-collapsed`** — Full viewport width, 44px tall. `{colors.surface-raised}` background, 1px `{colors.hairline}` top border. Compass icon button centred — the single tap target. Right end reserved for future "add to workspace" control.

**`chat-drawer-expanded`** — Expands upward to 52vh. Two-panel workspace inside, split 1fr 1fr:

**Left — conversation thread:** `{colors.surface-raised}` background. Messages labelled `YOU` and `COMPASS` in `{typography.mono-label}` / `{colors.muted}`. User messages right-aligned, white bg, hairline border. Compass messages left-aligned, `{colors.shell}` bg. Input bar at bottom: text field + send button, ⌘K hint in `{colors.faint}`.

**Right — output panel:** `{colors.canvas}` background. White header with `{colors.hairline}` bottom border: `OUTPUT` label left in `{typography.mono-label}` / `{colors.faint}`, tab row right (Diff | Diagram | Canvas) + share icon. Body: single dark code card (`{colors.surface-dark}`, `{rounded.code}`), code card header carries filename + diff badge (`+8 / −3`).

---

## Do's and Don'ts

### Do
- Anchor every surface on `{colors.canvas}` (#FDFCFB). White (`{colors.surface-raised}`) is only for raised elements — topbar, cards, chat bar.
- Use Newsreader for every headline. Pair with Public Sans body. Negative letter-spacing on all Newsreader display sizes is non-negotiable.
- Keep `{colors.primary}` (emerald) scarce. Active left borders, ID badges, callout box accents. Not button fills, not hover backgrounds, not decorative accents.
- Use `{colors.surface-dark}` for code blocks only. Never as a panel background, never as a card variant.
- Keep all four columns visible simultaneously. No modals, no overlays, no routing.
- Ghost-weight borders everywhere. The layout holds without visual noise.

### Don't
- Don't use cool grays or pure white as a page background. The warm cream is the defining surface choice.
- Don't use a second accent colour. Emerald is the only accent. Category colours or status colours are not in this system.
- Don't round corners beyond 8px. The interface is structured and editorial — excessive rounding undermines it.
- Don't put JetBrains Mono on prose or UI labels. Mono appears only where it earns it — code, IDs, structured labels.
- Don't add hover shadows to panels or columns. Depth is surface colour, not floating elevation.
- Don't overlay elements. Every component occupies its own clean spatial zone.
- Don't use the dark surface outside of code blocks. The cream-to-dark contrast is a deliberate editorial moment — not a general UI pattern.

---

## Responsive Behaviour

Compass is a desktop-first four-column layout. Below 1024px the layout collapses:

| Breakpoint | Behaviour |
|---|---|
| Desktop (> 1024px) | Full four-column layout. All panels visible. |
| Tablet (768–1024px) | Nav strip + section list collapse to a bottom tab bar. Detail and rules panels stack. |
| Mobile (< 768px) | Single column. Nav strip becomes bottom tab bar. Section list, detail, and rules panel are separate views. Chat drawer becomes a bottom sheet. |

Touch targets minimum 44px on all interactive elements at mobile breakpoints.
