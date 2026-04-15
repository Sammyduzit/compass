# Compass — Building on What Already Works

> **Team 4 — Stuart McLean**
> **Status:** Strategic recommendation — for whole team discussion
> **Question this answers:** What proven approaches from competitors should we adopt and adapt, and in what order?

---

## The principle

Don't invent what's already been proven. Identify what each competitor does best, adopt that approach, then layer on what they couldn't or didn't do. Build on the shoulders of what works.

The competitive research shows a clear progression. Each tool in the market solved one part of the problem well and left the next part open. Compass's job is to walk that path — adopting each proven step and adding the one thing nobody else did.

---

## The progression

### Step 1 — Adopt from Mapstr: one command, one folder, zero friction

**What Mapstr proved:** A CLI tool that runs against any repo, produces files in a folder, and requires no setup beyond installation is the right delivery mechanism for this problem. The one-command philosophy works. Developers adopt it because there's no friction.

**What we take:**
- Single binary CLI, one command to run
- Output to a folder inside the target repo
- Multi-provider LLM support (Claude, OpenAI, etc.)
- Structural parsing as the starting point for analysis
- Watch mode for regeneration on file changes (future)

**What Mapstr missed that we fix:**
- It sends the whole repo in one blob — we use FileSelector
- It produces one summary — we produce structured clusters with citations
- It has no conventions layer — that's our entire value proposition
- It has no Phase 1/Phase 2 separation — so every run costs LLM tokens

**The lesson:** Mapstr validated the market and the delivery mechanism. We take that and go deeper.

---

### Step 2 — Adopt from Swimm: static analysis before LLM, validator after

**What Swimm proved:** The highest quality AI documentation output comes from a three-step pipeline — deterministic static analysis first, LLM generation grounded in that analysis, validator checks output against the analysis. This is the most sophisticated hallucination guard in the market.

**What we take:**
- Phase 1 (collectors) runs before any LLM call — we already have this
- Every LLM call is grounded in actual code, not free-form generation
- Prompt design enforces "derive only from what you observed" — hallucination guard
- Output validation against source files — does this rule actually appear in the golden file?

**What Swimm missed that we fix:**
- Swimm requires human authoring — we derive automatically
- Swimm lives in the IDE — we produce a shareable artifact
- Swimm documents what people write — we extract what the code actually does
- Swimm has no conventions extraction — that's ours

**The lesson:** Swimm's pipeline architecture is the right approach to trust and quality. We adopt the principle — analysis grounds generation — and apply it to automated extraction.

---

### Step 3 — Adopt from Greptile: codebase graph as the intelligence layer

**What Greptile proved:** A repository-wide dependency graph — every function, class, file, and relationship — produces dramatically better output than sending raw source. The graph understands *why* files matter, not just what they contain. Greptile catches issues that diff-only tools miss because it sees the whole system.

**What we take:**
- `import_graph` — centrality scoring from directed import relationships (Team 1 already proposing this)
- Logical coupling from git history — files that always change together reveal hidden dependencies
- Multi-signal file scoring — churn + centrality + coupling = FileSelector
- The insight that context quality determines output quality, not prompt cleverness

**What Greptile missed that we fix:**
- Greptile produces no persistent artifact — everything is per-PR, per-query
- Greptile is for PR review, not onboarding
- Greptile has no conventions extraction
- Greptile requires an API key and accumulates cost — we use the CLI subprocess

**The lesson:** Greptile proved that graph-based file selection beats blob compression. FileSelector is our implementation of that principle, applied to onboarding rather than PR review.

---

### Step 4 — Adopt from Swimm (again): provenance per claim

**What Swimm proved:** Trust is built by linking every claim to its source. Swimm links every doc to the specific code block it was derived from. Developers can verify in one click. This is the only trust mechanism that actually works.

**What we take:**
- `golden_file` per cluster — every rule cluster links to the best example file
- Source citation per rule — every rule is grounded in observable code
- "Derived from, not invented" as a core prompt constraint
- Confidence signals — rules observed in many files vs one file feel different

**What Swimm missed that we fix:**
- Swimm's citations require human authoring — ours are derived automatically
- Swimm cites within the IDE — ours are in a shareable artifact anyone can open
- Swimm has no conventions — ours is the entire output

**The lesson:** Provenance is not a feature, it's the foundation of whether anyone trusts the output. We build it in from day one.

---

### Step 5 — Adopt from Mintlify: the experience layer as a first-class concern

**What Mintlify proved:** The interface through which people consume information is as important as the information itself. Mintlify turned documentation from markdown files into beautiful, searchable, AI-queryable experiences. Their growth from 7-figures to 8-figures ARR in one year is proof that developers will pay for information that is actually usable, not just technically correct.

**What we take:**
- Output designed for how people actually consume information — not just how it's easiest to generate
- Search as a first-class feature — find what you need, don't scroll through everything
- Structured format that both humans and machines can consume
- The idea that documentation is an interface, not a file

**What Mintlify missed that we fix:**
- Mintlify needs humans to write the source — we derive automatically
- Mintlify is a hosted platform — we are local, zero friction
- Mintlify documents external APIs — we document internal team conventions
- Mintlify has no conventions extraction

**The lesson:** The experience layer is not an afterthought. It's what determines whether anyone uses the output. We design for the person holding it, not the developer building it.

---

## The full adoption path visualised

```
Mapstr          →  One command, one folder, zero friction
    +
Swimm (pipeline) →  Static analysis grounds LLM generation
    +
Greptile        →  Graph-based file selection beats blob compression
    +
Swimm (trust)   →  Provenance per claim builds trust
    +
Mintlify        →  Experience layer is a first-class concern
    =
Compass         →  Automated, cited, versioned conventions
                    with an experience layer designed for humans
```

Each step adds what the previous tool couldn't do. Nothing is invented from scratch. Everything is proven.

---

## What this means for the build order

**v1 — prove the pipeline**
Adopt Mapstr's delivery mechanism. Adopt Swimm's pipeline architecture. Adopt Greptile's graph-based selection. Produce `rules.yaml` and `summary.md` with source citations. This is the uncontested position — no tool does this.

**v1.5 — prove the trust**
Adopt Swimm's provenance model fully. Add confidence signals. Add explicit gap detection. Validate every rule against its golden file. This is what makes developers actually trust the output.

**v2 — prove the experience**
Adopt Mintlify's philosophy. Build the local web UI. Make every rule clickable, every golden file a link, every gap visible. Add the "explain this to me" interaction. This is what makes it something people share.

**v3 — the uncontested position fully realised**
Everything above, plus the architecture diagram, plus the skill adapter, plus language-specific templates. The thing nobody else has even attempted.

---

## The one sentence version

> We are not building from scratch. We are taking the delivery mechanism Mapstr proved, the pipeline architecture Swimm proved, the graph intelligence Greptile proved, the trust model Swimm proved, and the experience philosophy Mintlify proved — and connecting them into the one thing none of them built: automated, citable, versioned team conventions with a human experience layer on top.

That is not a moonshot. Every component has been proven. We are assembling them in a sequence nobody else has assembled.
