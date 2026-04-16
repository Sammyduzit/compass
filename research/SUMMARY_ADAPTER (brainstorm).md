# Summary Adapter 

> **Team 4 — Paula Schweppe / Stuart McLean **
> **Status:** Brainstorm only — nothing to build yet
> **Context:** Last day of planning. Feeds into prompt design and adapter architecture decisions.

---

## The task

Own the SummaryAdapter output. Define what the summary contains and how it adapts to different onboarders. Open questions: is it a flag, auto-detected, or interactive? One file or many? What does each audience actually need?

---

## Question 1 — How does level get determined?

Three options considered:

**`--level junior|mid|senior` flag**
Explicit, consistent with Compass CLI design. Problem: people don't self-assess accurately relative to a specific codebase. A senior dev joining a repo in an unfamiliar domain is effectively junior to *that* repo. The flag asks the wrong question.

**Auto-detected**
Not feasible in v1. Would require knowing who's running it — Compass doesn't have that information. A `.compass/user.yaml` config is possible but adds friction.

**Interactive pre-run question**
Off the table. DECIDED.md is explicit: Compass is non-interactive. Runs through, produces files, exits.

**Recommendation: `--depth shallow|standard|deep`**
Reframe from "who are you?" to "what do you want from this output?" This works for everyone — an experienced dev joining a new domain picks `deep` not because they're junior but because they want the full picture. Consistent with Compass's existing CLI flag pattern.

---

## Question 2 — One file or separate files per depth level?

**Case for separate files:** different audiences, different cognitive load. A junior hitting architecture trade-off sections on day one is noise.

**Case for one file:** the summary is a team artifact. One thing to version, one thing to link, one thing to point a new hire at.

**Recommendation: one file, layered structure**

The structure does the adaptation work. Sections are ordered from orientation to depth. A junior reads the top three sections and has enough to start. A senior reads the whole thing in five minutes.

```
summary.md
├── What this codebase is          (all depths)
├── What to read first             (all depths)
├── The patterns                   (all depths, depth controls detail)
├── Gotchas and traps              (all depths)
├── Architecture decisions + why   (standard + deep)
├── Load-bearing abstractions      (deep only)
└── What the git history reveals   (deep only)
```

This also maps cleanly to `summary.json` — each section is a named field, not free-form prose. The UI can render sections selectively. **`summary.json` should be generated alongside `summary.md` from day one** — noted in UX_BRIEF as a key architecture decision. Zero extra cost at adapter time, significant cost to retrofit later.

---

## Question 3 — What does each audience actually need?

The right frame: not "what information exists" but "what question is this person trying to answer."

**Shallow / first week — orientation and safety**
- What is this? (one paragraph, plain English, no jargon)
- How is it shaped? (concepts, not a folder tree)
- What should I read first? (ordered list, one-sentence reason per file)
- What will trip me up? (gotchas from git history + docs collector)
- What does a typical feature look like? (the repeating unit of the codebase)

**Standard / mid-level — understanding, not just operating**
- Everything above, compressed
- Why does it work this way? (reasoning behind patterns, not just what they are — pulls from `why` field in rules.yaml)
- What are the non-obvious choices?
- Where does complexity live? (coupling hotspots, high-churn files)

**Deep / senior — risk and leverage**
- Architecture decisions and what was rejected
- Technical debt signals (high churn + high coupling = interesting; stable + central = load-bearing)
- The abstractions everything depends on
- Coupling clusters not visible from imports — hidden dependencies

The three levels want different *framings* of mostly the same underlying data. The AnalysisContext already has what's needed. The prompt doesn't need different data per depth — it needs to emphasise different signals and frame them differently.

**Implication:** one SummaryAdapter, one prompt template, with a `depth` parameter. Not three separate adapters.

---

## Question 4 — One call or two?

**What one call has to do:**
Orientation paragraph, read-first list, patterns overview, gotchas, architecture decisions, load-bearing abstractions. These are epistemically distinct — compression, inference from git signals, negative pattern extraction. One call can do all of this, but tends toward evenly mediocre output rather than genuinely good output on any single section.

**The case for two calls:**

Call 1 — Structural synthesis (analysis, not writing)
- Input: file scores, coupling pairs, import graph, git patterns
- Output: structured JSON intermediate — which files are load-bearing, what coupling clusters reveal about module boundaries, what churn implies about complexity

Call 2 — Human-facing generation (writing, not analysis)
- Input: code skeleton + docs + patterns + output of Call 1
- Output: summary.md sections, depth-adapted

Call 2 has pre-digested input. The gotchas section is rendering a pre-computed list, not inferring from raw git signals. Easier task, better output.

**The architectural frame:** this is not one adapter making two calls. It is two adapters — `StructureAdapter` (produces `architecture_synthesis.json` as an intermediate) and `SummaryAdapter` (consumes it). Keeps the one-call-per-adapter rule. The intermediate is reusable — DocsAdapter and SkillAdapter benefit from the same structural synthesis.

```
AnalysisContext
    │
    ▼
StructureAdapter (Call 1)
    → architecture_synthesis.json   ← intermediate, not a final output
    │
    ▼
SummaryAdapter (Call 2)
    → summary.md + summary.json

RulesAdapter also benefits from architecture_synthesis.json
DocsAdapter (future) same
```

**v1 honest answer:** one well-structured call probably clears the bar. The AnalysisContext Team 1 is proposing already pre-digests enough that the model is not doing raw inference. But design the adapter interface now so the two-call split is possible without a rewrite. Concretely: SummaryAdapter's `context_sections` should include a slot for `architecture_synthesis` even if that slot is empty in v1.

---

## On prompt design

The concern: without experience knowing where to look or what to ask, the natural default is "write a summary" — which is exactly the prompt that produced a hallucinated rule in v0.

**Three things a good prompt does instead:**

1. **Tells the model what to look at, not just what to produce**
Not "summarise this codebase" but "given the file scores below, identify the three files with the highest centrality and explain in one sentence each why they are load-bearing."

2. **Forces grounding before generation**
"First list the coupling clusters you can see in the data. Then use only those clusters — not your general knowledge — to describe the module boundaries." The model shows its working before writing prose. Hallucinations become visible.

3. **Defines done in the schema**
If output is `summary.json` with named fields, the model cannot produce a fluent-but-wrong blob. It has to populate `orientation`, `read_first`, `gotchas` — and if `gotchas` is empty it says so explicitly rather than inventing one.

The prompt is a routing table: need → data source. Each section of the summary maps to specific fields in the AnalysisContext. That mapping is the skeleton of the prompt.

---

## Open questions for the team

| Question | Why it matters | Who decides |
|---|---|---|
| `--depth` vs `--level` — does framing it as "what you want" vs "who you are" land better? | Affects CLI design and whether the flag gets used correctly | Whole team |
| Does `summary.json` get generated alongside `summary.md` from day one? | Retrofitting is expensive. Doing it now costs almost nothing. | Team adapters |
| Does the gotchas section come from git collector, docs collector, or both? | Determines what AnalysisContext fields SummaryAdapter declares as inputs | Team 1 + Team 2/3 |
| "What was rejected and why" for senior depth — does this require semantic git reading (`git_semantics`)? | If yes, it is v2 scope, not v1 | Whole team |
| Does StructureAdapter make sense as a named intermediate in v1, or is it premature? | Affects adapter count and pipeline complexity | Whole team |

---

## Brainstorm questions from BRAINSTORM.md covered here

**Q4 — Developer experience**
- First thing a new dev wants: orientation, then navigation, then traps. In that order.
- Output format: markdown for humans, JSON alongside it for machines and UI. Both.
- Trust: every claim traceable to a source file. Gaps surfaced explicitly, not papered over.

**Q5 — What does a good prompt look like**
- Include specific data fields, not just the codebase blob
- Prevent hallucinations by forcing grounding before generation and defining output schema strictly
- Prompt should vary by depth parameter, not by repo type in v1
- Iterate on prompts without re-running full pipeline: SummaryAdapter is independently re-runnable once AnalysisContext exists

**Q6 — Right scope for v1**
- Minimum viable SummaryAdapter: one call, `shallow` depth only, `summary.md` + `summary.json`, grounded in AnalysisContext
- Language support: TypeScript/Node first, generic fallback prompt
- "Done" for SummaryAdapter: output that a new developer would actually read on day one — not a YAML file, not a wall of text
