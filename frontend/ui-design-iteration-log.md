# Compass UI — Design Iteration Log
_Local only. Not tracked in git._

---

## v5 — 2026-05-08

**Action:** `research/Mockup/compass_mockup_v4.html` renamed and moved to `docs/Mockups/compass-v5.html`.

**Reason:** All mockups belong in `docs/Mockups/`. The `research/` folder was never the right home. The file content is unchanged from the end of the 2026-05-07 polish session — this is a relocation, not a design revision. The v4 file in `docs/Mockups/compass-v4.html` is the pre-polish earlier iteration and is kept as historical reference.

**Live mockup:** `docs/Mockups/compass-v5.html` — open directly in browser.

---

## Session: 2026-05-05

### Starting point
`compass_mockup_v2.html` — a single-column scroll design with:
- Topbar, summary bar, 4 metric cards
- Search input with intent-mapping
- Bento grid of cluster cards
- Rules panel (click cluster → rules appear below)
- "Read first" file list at bottom

**Decision:** Discarded. This design did not match the agreed 3-column layout from the previous session, had no chat, and was built without using any design skills.

---

### v3 Mockup — `compass_mockup_v3.html`

**Built:** 2026-05-05 using the `high-end-visual-design` skill.

**Design choices:**
- Font: Plus Jakarta Sans (not Inter/Roboto)
- Palette: Soft Structuralism — warm off-white `#F8F7F5`, clean white surfaces, emerald accent `#18794E`
- Layout: 3 columns — narrow nav (272px) | detail panel (flex) | rules panel (308px)
- Cascading interaction: click card in Col 1 → Col 2 populates detail → Col 3 populates filtered rules
- Chat: floating bubble bottom-right, expands to small window
- "Tell me more" / "Ask about these rules" chips on each panel to pre-populate chat

**Stuart's feedback on v3:**

| Issue | Detail |
|---|---|
| Missing true nav column | No dedicated left nav strip. Col 1 showed items but no section-level quick-jump. On large codebases, scrolling through 20+ items to find one is painful. |
| No progress tracking | No way to mark items as seen or bookmark them for later. |
| Redundant chat triggers | Floating bubble in bottom-right + chips in panels = same action offered twice, looks cluttered and silly. |
| Chat placement | Full column for a chatbox is wasteful. Suggested: collapsible horizontal row instead. |
| Chat trigger pattern | Replace scattered chips with a single standard: Compass logo icon button, consistent position on every card (top-right). |

---

### Agreed direction for v4

**Layout (4 zones):**
```
[ Nav strip ] [ Item list ] [ Detail panel ] [ Rules panel ]
    narrow       ~220px          flex             ~300px
```

1. **Nav strip (far left, tight)** — section labels: What it does, Start here, Stable, Hotspots, Clusters. Collapsible tree. Clicking jumps to section / item without scrolling.
2. **Col A** — item cards for the active section
3. **Col B** — rich detail for the selected item (explanation, concepts, context)
4. **Col C** — contextually filtered rules for the selected item

**Chat:**
- Collapsible horizontal row (drawer-style), not a corner bubble
- Expands upward when opened
- Acts as search/command window, not just Q&A
- Exact scope (one column vs full-width) — **TBD, pending Stuart's answer**

**Chat trigger:**
- Single Compass green logo icon button on each card/panel, standard position (top-right)
- Clicking opens chat with that item's context pre-loaded
- All chips removed

**Progress tracking:**
- Tick/checkbox on nav items to mark as seen
- Bookmark feature (future)

---

### Open questions (Stuart to answer)
1. Does the far-left nav expand inline (tree with sub-items), or does clicking a section just activate it while Col A renders the items?
2. Does the collapsible chat row live inside one specific column, or span the full workspace width?

---

### Files created this session
- `research/Mockup/compass_mockup_v3.html` — current working mockup (local, not committed)
- `docs/ui-design-iteration-log.md` — this file

---

## Session: 2026-05-07

### Context
With the v4 layout direction agreed, this session shifted focus to visual identity — exploring what Compass should *feel* like, not just how it should be structured. Five generated design variants existed in Stitch (under project "Compass", formerly "Variation Generator Suite"), each exploring a different aesthetic angle.

### Screens reviewed

| Screen | Theme | Notes |
|---|---|---|
| The Manuscript (Refined Layout) | Warm editorial, cream bg, serif headline | Strongest visual identity |
| Soft Light Refined | Clean 3-col SaaS, sans-serif | Best structural bones, weakest personality |
| Soft Light Edition | Similar to Refined, earlier iteration | Superseded by Refined |
| Deep Ink Edition | Dark mode, green accent | Best content structure; palette too harsh |
| Minimalist Flow | Light, docs-site scroll | Generic copy, forgettable layout |

### Design decision: The Manuscript as visual foundation

**The Manuscript** was chosen as the primary design language for Compass v4. The rationale:

- The warm cream background (~#FDFCFB) immediately signals this is a *reading and thinking* environment, not a dashboard or analytics tool. It positions Compass alongside editorial software rather than DevOps tooling.
- The large serif headline with italic emphasis (*everything*) demonstrates typographic intentionality — rare in developer tools, which tend toward uniform sans-serif. It earns attention before a word is read.
- The editorial breathing room — generous margins, no competing panels — communicates that the content itself is the product. Compass surfaces insights; The Manuscript's layout treats those insights with appropriate weight.
- The dark code block contrasted against the cream background has a physical quality, like ink on paper.

**What The Manuscript lacks** (and where we borrow from other screens):

| Missing element | Source | Rationale |
|---|---|---|
| Left nav strip + section hierarchy | Soft Light Refined | Orientation and quick-jump are essential at scale |
| Associated rules panel (right col) | Soft Light Refined + Deep Ink | Rules are a primary output; they need persistent visibility |
| Tag pills (Entry Point, Inversion of Control) | Deep Ink | Communicates the type of a file or concept at a glance |
| "Why this matters" callout boxes | Deep Ink | Elevates explanation above raw description — editorial voice |
| File tree context in nav | Deep Ink | Grounds abstract sections in actual code paths |

### Night mode direction

Night mode will use the Deep Ink structure with the design system's #18794E emerald replacing the harsh bright green. The cream background inverts to the dark surface token stack. The palette becomes muted and intentional rather than GitHub-derived.

### Copy direction

All placeholder copy referencing generic "TypeScript services" is to be replaced with Compass-specific language throughout:
- "What Compass found" not "Getting Started"
- "Start here" / "Hotspots" / "Stable" / "Rule clusters" as the nav vocabulary
- Associated rules referenced by their real IDs (DI-01, HEX-04, etc.)
- Tone: precise, authoritative, developer-native — no marketing language

### Next step
Build the synthesised v4 screen in Stitch: Manuscript editorial language + 3-column structure from Soft Light Refined + content components from Deep Ink.

### Artefact: compass_mockup_v4.html

Built directly as HTML rather than via Stitch generation (Stitch timed out on three attempts — the layout complexity exceeded its generation window). Building by hand gave us exact control.

**File:** `research/Mockup/compass_mockup_v4.html`

**What's implemented:**
- Full four-column layout: icon nav strip (56px) | file list (220px) | main detail (flex) | rules panel (296px)
- Topbar: Compass serif wordmark + repo/branch context + timestamp + avatar
- Icon nav strip with active-state emerald indicator, completion ticks, settings at bottom
- File list with active item emerald border — `src/make-app.ts` selected
- Main detail: breadcrumb → tag pills → Newsreader headline with italic → body copy → "WHY THIS MATTERS" callout → dark code block (TypeScript DI factory, syntax highlighted) → prev/next footer
- Rules panel: DI-01 / HEX-04 / COMP-02 rule cards with emerald ID badges, "golden file" label, "View all 12 rules" footer
- Chat drawer: 44px collapsed bar, full-width, compass icon + placeholder + ⌘K shortcut
- Google Fonts loaded: Newsreader (serif) + Public Sans (body) + JetBrains Mono (code)
- Design tokens: cream #FDFCFB, emerald #4A7862, slate-dark #1E2329, ghost borders, ambient shadows

**Status:** v4 direction complete as static mockup. Next step: resolve the two open questions (nav expand behaviour, chat scope), then begin React implementation in `ui/`.

---

## Session: 2026-05-07 (continued — v4 feedback round 1)

### Feedback on compass_mockup_v4.html

**Layout:**
- Shell expanding to full viewport width looks wrong at wide screen sizes. Needs max-width: 1440px, centered. Standard desktop app convention.
- Exception: the chat workspace at the bottom should break out of the constraint and maintain full viewport width — preserving the large work surface.

**Interactivity:**
- Breadcrumb and tag pills (ENTRY POINT, INVERSION OF CONTROL) must be clickable — cursor:pointer, hover states. They imply navigation.

**Navigation strip:**
- Icon choices are unclear — the tick mark and star positioned under each other read as decorative, not functional.
- "What it does" must be the landing/first view — not "Start here". File names (src/make-app.ts) are meaningless to a newcomer as a first impression. Step zero is orientation: what does this codebase actually do?

**Content ↔ Rules connection:**
- There is no visual link between a paragraph the user is reading and the rules it references. Needs a hover/highlight mechanism so the user understands which rule is relevant to which piece of content.

**Topbar — full redesign:**
Previous: Compass wordmark | repo + branch (centre) | timestamp + avatar (right)
New direction:
- LEFT: Compass wordmark + repo name + branch pill hugged together
- CENTRE: Three primary navigation tabs — **Onboarding** | **Workspace** | **Community**
- RIGHT: Settings icon + avatar only

**Product expansion — Onboarding / Workspace / Community:**
This is a significant product decision, not just a UI one. The three tabs define three distinct modes:
- **Onboarding** — code exploration (current view). Understand the codebase.
- **Workspace** — personal notes, saved items, session history. Do your work.
- **Community** — team directory, org hierarchy, contacts, Slack invites, notice board. Meet your people.

The insight: a new hire is not just onboarding with a codebase — they are onboarding with an organisation. Compass can hold both. This positions Compass as a full new-hire onboarding platform, not a developer tool.

Mental model of the three tabs: *understand the code → do your work → meet your people.*

**User context in section list:**
User's name and current project should appear at the top of column 2 (section list), above the section headers — personalising the workspace and making it clear whose onboarding session this is.

---

## Session: 2026-05-07 (continued — v4 final polish round)

### Changes applied to `compass_mockup_v4.html`

**Topbar — repo pill repositioned**
The repo/branch pill (`service-api`) was moved from the top-left (adjacent to the wordmark) to the top-right, sitting next to the avatar. This keeps the left side clean (wordmark only) and groups repo context with the user identity controls where it belongs.

**Detail column — centering fixed**
Content in the middle detail column was not receiving equal padding on both sides. Root cause: `padding %` resolves against the *parent* container width (the full shell), not the column width — so `6.5%` of 1440px gave ~94px on one side instead of the intended 58px. Fixed by removing all horizontal padding from `.main-detail` and using a single inner wrapper with `width: calc(100% - 116px); margin: 0 auto`. This gives exactly 58px each side at any viewport width and is fully responsive.

**Chat drawer — reverted to X1 reference layout**
The chat drawer was reverted to match the `X1.png` reference: proper YOU / COMPASS message labels, correct bubble styling on the left thread panel, full-width workspace split evenly 50/50 (`1fr 1fr`).

**Output panel (right side of chat)**
Implemented to match `chatbox-right-terminal.png`:
- Background: light cream (`--cream`)
- Header: white (`--white`) with `OUTPUT` label (left, mono, faint) + `Diff / Diagram / Canvas` tabs (right) + share icon
- Body: 12px padding all around, contains a single dark rounded code card (`border-radius: 6px`, `--slate-dark`)
- Code card header: filename + diff badge (`+8 / −3`)

**Flexbox layout bug — output header disappearing**
The output panel header was rendering correctly on first paint but immediately being pushed out of the visible area. Root cause: the `output-code-block` with `flex: 1` was growing to its intrinsic content height (larger than the workspace), overflowing the grid cell, and the workspace's `overflow: hidden` was clipping the header off the top. Fix: added `min-height: 0` to `.chat-workspace`, `.chat-thread`, `.chat-output`, and `.chat-output-body`, plus `grid-template-rows: 1fr` on the workspace. This constrains the flex/grid tree so overflow is absorbed by the scrollable body, not pushed onto the header.

### State of mockup at end of session
`compass_mockup_v4.html` is complete and visually stable:
- Four-column layout with topbar, icon nav, file list, detail, rules panel
- Chat drawer: collapsed 44px bar → expands to 52vh full-width workspace
- Left thread panel: clean white, YOU / COMPASS message labels, conversation bubbles
- Right output panel: cream body, white header with tabs, dark code card inside
- Paragraph → rule hover highlighting wired up
- All topbar, nav, and content interactions functional
