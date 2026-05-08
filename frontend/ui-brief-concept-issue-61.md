# Compass UI — Design & Architecture Brief
### Issue #61 — Frontend Scaffold

---

## Overview

This brief covers the architectural and design decisions for the Compass v2 frontend before implementation begins. It is intended to align the team on approach before code is written.

---

## 1. Layout — Three Columns, Not Tabs

Compass has exactly three distinct data surfaces: the summary, the rules, and the chat. The layout expresses that directly.

```
┌──────────────────────────────┬──────────────────────────┬───────────────┐
│  ▌ What it does              │                          │               │
│  · Start here                │   Rules                  │   Chat        │
│  · Stable                    │   (static)               │   (persistent)│
│  · Hotspots                  │                          │               │
│  · Clusters                  │   Cluster cards          │   Always on.  │
│  ──────────────────          │   Rule details expand    │   Always has  │
│                              │   inline on click.       │   full context│
│   <section content>          │                          │               │
│                              │                          │               │
└──────────────────────────────┴──────────────────────────┴───────────────┘
```

No React Router. No tab toggle. No hard switching between views.

The reason this works: the layout maps one-to-one to the product's actual structure. Summary is the reading anchor. Rules is the convention reference. Chat is the always-available question layer. Three panels, always mounted, always accessible.

### Summary panel — vertical section nav

The Summary panel has five fixed sections. A slim vertical nav lives on the left edge of the panel — a chapter list, not a tab system. Five items stacked, active section highlighted, the rest muted. Click one to jump; scroll naturally and the active item updates.

This is not a separate layout column. It is part of the Summary panel. On the primary desktop viewport it sits as a ~48px bookmark strip. The full section content is always present and scrollable — the nav is a map, not a gate.

Counts and indicators can live here without crowding prose: hotspot count, cluster count. Useful orientation signal before the developer has read a word.

This also feeds the Phase 2 reactive rules upgrade: the active section is already a first-class signal. When the developer is in "Clusters", that's the trigger for the Rules panel to surface the right cluster cards.

### Why not React Router

React Router is the right tool when you need shareable URLs, browser history, or independent page lifecycles. Compass UI needs none of these. It is a local analysis dashboard for a single repository.

With a router, each route manages its own data lifecycle. Sharing state between routes requires either a global store or prop-drilling through the route tree — both of which add complexity for no user-facing benefit.

With always-mounted panels, `summary.json` and `rules.yaml` load once at the `App` level. All three panels have access immediately and always. State is trivial. Chat always knows what's loaded.

If deep-linking ever becomes a genuine requirement, it can be dropped in. Starting with a router and trying to retrofit persistent panels and shared state is the harder path.

### Phase 2 — Reactive Rules (not in scope for scaffold)

The three-column layout is a foundation, not an endpoint. The natural evolution: the Rules panel becomes context-aware. As you read a section of the summary (hotspots, a cluster, a stable file), the Rules panel surfaces the conventions that apply to what's visible.

Rules contracts to a slim reference strip when the developer is reading. It expands when they need it. It's not a hard panel switch — it's a reactive companion.

This is the right final direction. It is not the right starting point. The scroll-tracking, semantic coupling, and dynamic filtering are non-trivial to get right before the API even exists. Build the static version. Get it working. The reactive layer follows.

---

## 2. Chat Interface

The chat panel is not a future feature. It is the product completing itself.

By the time the UI loads, Compass has already produced a complete knowledge base about the repository:

- `summary.json` — what the codebase does, what is safe to touch, what is moving, how the pieces connect
- `rules.yaml` — every convention, pattern, and architectural decision extracted from the actual code

A developer on day one has questions. Most of them are already answered in this data:

> *"What should I read first?"*
> *"Is it safe to touch the auth layer?"*
> *"Which files change together?"*
> *"What is the error handling convention here?"*

For simple queries the answers come from the structured data directly — no LLM call needed. For deeper reasoning, the context is passed to Claude and the response is grounded in what Compass actually found, not hallucinated general knowledge.

The chat panel is persistent. It is always present, always has access to both loaded data sources, always knows which section of the summary is active. This is the correct UX for a tool whose job is to answer questions about a codebase.

This also positions Compass as a product, not just a CLI utility. The CLI produces the knowledge. The UI makes it conversational and explorable.

---

## 3. The Entry Moment

The layout is the reading environment. The entry moment is a separate design decision that sits on top of it.

The proposal: when the UI first loads, it does not open directly into three columns of data. It opens with a focused, calm entry screen. The developer types their name — possibly their role. The interface comes to life around that input. The greeting in the summary is tailored. The chat knows who it is talking to.

This is the Focus Reveal pattern: the interface earns the developer's attention before demanding it.

**This is an open design question for the scaffold phase.** The entry moment is worth getting right, and it connects to the longer-term persona-aware output idea (where role/experience shapes the voice of what Compass produces). For now, it is flagged as a design decision that needs to be made before templates are written, not after.

Options:
- Simple name input, no role — minimal friction, personalises greeting only
- Name + role selector — connects to future persona-aware output, adds one step
- No entry screen — load directly into the three-column view, entry moment is a v2 concern

---

## 4. Design Direction

### The problem with the terminal aesthetic

The reflex in developer tooling is dark backgrounds, monospace everything, high contrast, colour-coded severity. This aesthetic communicates: you are in a coding environment.

Compass is not a coding environment. It is a reading environment. The output is prose and structured data. A developer reads `summary.md` the way they read documentation — for orientation, not for syntax. The terminal aesthetic is the wrong reference.

It is also not a neutral choice. High contrast and harsh code blocks create fatigue during extended reading. Day one of a new codebase is already cognitively expensive. The UI should reduce that cost, not add to it.

### The reference: Claude.ai

Claude.ai works as a design reference because it does not feel like a tool. It feels like a place. Warm off-whites, generous whitespace, typography that does not fight you. It is calm. Calm is what a developer needs when they are anxious about a new codebase.

This is the direction for Compass:

**Warm neutrals as the base.** Cream and parchment tones rather than stark white or dark grey. The eye relaxes. Reading becomes sustainable. This is not a cosmetic choice — it is a readability choice.

**Typography first.** The content is the product. If the typography is right — readable size, generous line height, a humanist sans-serif for body text, monospace only where it earns it — the interface mostly takes care of itself. Monospace is for file paths, code examples, and rule IDs. Not for everything.

**Code blocks that do not shout.** A slightly deeper warm tone for code surfaces rather than harsh contrast boxes. The information is still distinct. The contrast is just not aggressive.

**One accent colour.** Used sparingly — active state, primary action, chat send button. Everything else is neutral. The accent carries the brand. The neutrals do the reading work.

**Weight and space over colour coding.** Most dev tools use colour to signal importance — red for errors, green for good. Compass uses weight and space instead. A hotspot file is not red — it is set with more breathing room and slightly heavier type. The information lands without the alarm. This is a deliberate departure from convention.

### Client theming

Compass will serve teams, agencies, and organisations with their own visual identity. The theming system needs to be first-class from day one, not retrofitted later.

The approach: CSS custom properties as a complete design token system.

```css
--color-surface-base       /* page background */
--color-surface-raised     /* cards, panels */
--color-surface-code       /* code blocks */
--color-text-primary
--color-text-secondary
--color-text-muted
--color-accent             /* brand colour — the one swap */
--color-border
--font-sans
--font-mono
```

A client provides their brand tokens. The entire UI shifts. Their logo, their palette, their feel. Compass becomes white-label ready without a redesign. The neutral base means almost any accent colour works — the system is designed to be overridden.

Dark mode, high-contrast mode, and client themes are all the same mechanism.

---

## 5. What This Breaks From

| Convention | Compass approach |
|---|---|
| Dark terminal aesthetic | Warm neutrals, reading-first |
| Colour-coded severity | Weight and space |
| Monospace everywhere | Monospace only where earned |
| Harsh code block contrast | Soft, warm code surfaces |
| Router-based navigation | Always-mounted panels, shared state |
| Tab switching between views | Three columns, all visible |
| Chat as a future feature | Chat as a persistent panel from day one |
| Fixed theme | Token system, client themeable |
| Reactive rules panel | Phase 2 — static first, reactive evolution follows |

None of these are arbitrary. Each one is chosen because Compass is a reading and orientation tool, not a coding environment. The design follows the function.

---

## 6. Build Sequence

1. Scaffold `ui/` with React + Vite + TypeScript
2. Build the token system and base theme first — everything else builds on top of it
3. Define TypeScript interfaces from `summary_schema.py` and `rules_schema.py` (hand-written until #62 lands)
4. Build `SummaryPanel` and `RulesPanel` against mock data
5. Wire the three-column layout with persistent `ChatPanel`
6. Decide on entry moment design (name input vs. direct load)
7. Replace mock data with API calls once FastAPI layer (#59) lands

**Phase 2 (after scaffold is stable):**
- Reactive Rules panel — scroll tracking in Summary, semantic coupling to cluster IDs, dynamic rules filtering
- Entry moment persona-awareness — role input shapes chat voice and summary emphasis
