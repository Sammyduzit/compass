# Onboring — Competitive Analysis

> **Team 4**
> **Authors:** Stuart McLean, Paula Schweppe
> **Status:** Findings complete — feeds into DECIDED.md and BRAINSTORM.md
> **Feeds into:** DECIDED.md (tooling decisions), BRAINSTORM.md (open questions)

---

## The problem we're actually solving

Most onboarding tools are built around one user: the new person who needs to learn.

We think the real problem has two users and two costs:

**The business cost** — onboarding a junior or intern can take six months. That's not just their time. It's senior dev hours interrupted, mistakes made while still learning the rules, re-work, and a long tail of "quick questions" that aren't quick. Companies are not getting rid of juniors — but they need them productive faster, with less drag on the people around them.

**The human cost** — being new is painful. Impostor syndrome. Not knowing what you don't know. Feeling like you're in everyone's way. Asking questions that feel stupid. The new dev doesn't just need information — they need to feel capable enough to actually do the job.

**Our hypothesis:** existing tools solve the business need (produce a document) but ignore the human need (make the person feel able to act). The gap is designing for both.

---

## Research question 1 — What do people actually do today?

Before tools, map the real workarounds — these are the true competition:

- Reading READMEs that haven't been touched in years
- Asking the one person who "knows everything" (and interrupting them constantly)
- Spending a week clicking around hoping patterns emerge
- Grep-ing for conventions nobody wrote down
- Asking AI assistants point questions with no persistent, shareable output
- Just guessing and breaking things

**Findings:**

The data confirms this is a real and costly problem, not anecdotal:

- **78% of new developers** find codebase navigation challenging or very challenging. 46% rate the difficulty 4 or 5 out of 5. — [JetBrains Platform Blog, March 2026](https://blog.jetbrains.com/platform/2026/03/the-experience-gap-how-developers-priorities-shift-as-they-grow/)
- **4–6 weeks** is the consistent benchmark for time-to-productivity without structured onboarding. With AI tools, this is beginning to compress — but only for teams that have already documented their codebase. — [DX Research](https://newsletter.getdx.com/p/developer-ramp-up-time-continues)
- **Senior developers lose 10–20% of their time** supporting a new hire over the first 2–3 months. With multiple team members involved, this translates to $8,000–$18,000 in diverted productivity per hire. — [DECODE Agency](https://decode.agency/article/hidden-costs-hiring-in-house-developers/)
- **36% of new developers** say their top documentation priority is introductory guides — compared to just 10% of experienced developers. The demand exists. The supply does not. — [JetBrains Platform Blog, March 2026](https://blog.jetbrains.com/platform/2026/03/the-experience-gap-how-developers-priorities-shift-as-they-grow/)

The pattern: existing workarounds transfer the cost of missing documentation onto the people least able to absorb it — the new dev and the senior they interrupt.

---

## Research question 2 — Where is the competitive gap?

Map existing tools across eight axes — automated, code-derived, produces a structured artifact, shareable with the team, conventions-aware (extracts actual coding rules and patterns), cites sources, signals confidence gaps, install friction:

| Tool | Automated | Code-derived | Structured artifact | Shareable | Conventions-aware | Cites sources | Signals confidence gaps | Install friction |
|---|---|---|---|---|---|---|---|---|
| Confluence / Notion | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | Low |
| Mintlify | Partial | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | Low |
| Swimm | ✗ | Partial | ✓ | ✓ | Partial | ✓ | ✗ | Medium |
| Greptile / Cosine | ✓ | ✓ | ✗ chat only | ✗ | ✗ | Partial | ✗ | Medium |
| GitHub Copilot / Cursor | ✓ | ✓ | ✗ ephemeral | ✗ | ✗ | ✗ | ✗ | Low |
| GitLoop | ✓ | ✓ | Partial | ✓ | ✗ | ? | ? | ? |
| DocuWriter | ✓ | Partial | ✓ | ✓ | ✗ | ? | ? | ? |
| Mapstr | ✓ | ✓ | Partial | ✓ | ✗ | ✗ | ✗ | Low |
| **Compass** | **✓** | **✓** | **✓** | **✓** | **✓** | **✓ planned** | **✓ planned** | **Low** |

**Note on Swimm — Conventions-aware: Partial.** Swimm extracts design patterns and links them to live code, with auto-sync when the code changes. However, it requires a human to author the walkthrough first — it does not derive conventions autonomously from the codebase. Compass does. That is the distinction.

**Findings:**

No current tool does all eight. The sharpest gap is Conventions-aware — no tool extracts coding rules automatically and outputs them as a structured, shareable artifact.

Additional UX gap: none of these tools are designed around how it *feels* to be new. They produce artifacts for the business. Onboring should be designed for the person holding it.

### Closest technical competitor: Mapstr

Mapstr is the most technically similar tool — CLI-based, fully automated, no manual input, code-derived. It produces a natural-language summary and dependency graph in seconds.

**What Mapstr is missing:** the Rules layer. It explains what the code does, not how the team works. No `rules.yaml`, no conventions, no `golden_file`. That single gap is where Compass sits.

**Why this matters:** Mapstr shows the idea is viable and there is demand. It also confirms the gap is real — people are already using it and still don't have their team's conventions documented.

### Closest market competitor: Swimm

Swimm targets the same user and the same problem — new developers who need to understand a codebase quickly. It focuses on "Continuous Documentation" — keeping docs linked to actual code so they don't go stale.

**Why someone might choose Swimm over Compass:**
- Human-authored walkthroughs are more accurate and nuanced
- Swimm embeds docs directly in the IDE
- More mature product, established trust

**Why Compass wins:**
- Zero authoring burden — no senior needs to write anything
- Derives from actual code, not what someone hoped to document
- Runs on any repo instantly, including ones with no existing docs
- Swimm requires someone to care enough to write the walkthrough. Compass works on repos where nobody did.

**Open question:** Is there a repo type or team size where Swimm's accuracy outweighs Compass's automation? Where does each tool break down?

---

## Research question 3 — What makes a new dev trust the output?

If someone runs Onboring and gets a `rules.yaml` — what makes them actually follow it? What signals "this is real and current" vs "this might be wrong"?

This directly affects design decisions: output format, whether it cites which files rules were derived from, whether it surfaces confidence or gaps, whether there's an interactive layer on top of the static files.

**Findings:**

The trust problem is structural, not incidental:

- **96% of developers do not fully trust AI-generated output.** This applies to code — for rules and documentation, the bar is higher because errors are less visible. — [The New Stack](https://thenewstack.io/agentic-ai-verification-impact/)
- **The primary trust mechanism is provenance** — the ability to trace every claim back to its source. MIT research (ContextCite) shows that trust increases when users can verify any statement by seeing exactly what context it was derived from. — [MIT News, 2024](https://news.mit.edu/2024/citation-tool-contextcite-new-approach-trustworthy-ai-generated-content-1209)
- **58% of developers use AI alongside technical documentation** to verify AI output. They are not replacing verification — they are adding an extra step. A tool that makes verification effortless removes this burden. — [Stack Overflow, March 2026](https://stackoverflow.blog/2026/03/16/domain-expertise-still-wanted-the-latest-trends-in-ai/)
- **65% say AI misses context** during refactoring and test generation. Rules without a "why" feel arbitrary and get ignored. — [SoftwareSeni](https://www.softwareseni.com/why-developer-trust-in-ai-coding-tools-is-declining-despite-rising-adoption/)

**What this means for Compass:**

Compass has a structural answer already built in: `golden_file`. Every rule in `rules.yaml` is linked to the file it was derived from. The new dev can verify any rule in seconds — not by searching, but by following a direct pointer to the source code. This is provenance. No other tool in the matrix offers it at the rule level.

Additionally:
- The `why` field on every rule is not optional — rules without reasoning get ignored
- Explicit gaps ("we could not find a clear convention for X") are better than hallucinated rules
- The v0 pipeline already produced one hallucinated rule (test-05 Given/When/Then) — this is a known risk, not a hypothetical

**If a junior follows a hallucinated rule and breaks something, their impostor syndrome doesn't just return — it doubles.**

---

## Tooling question (overlaps with Team 1 — Janis & Martins)

The whiteboard flagged: *"research better alternatives / lower usage"* next to the current ingestion tools. This is in our scope too.

**Current ingestion stack:**

| Tool | What it does | Question |
|---|---|---|
| `codebase-memory-mcp` | Architecture graph, relations | Is this the right tool or just the familiar one? |
| `repomix` | Compresses codebase ~4-5k tokens | Are there lighter alternatives with equivalent signal? |
| `codebase-context` | Git history, team patterns | What's the actual cost and where is the waste? |

**Alternatives identified:**

| Tool | What it does differently | Verdict |
|---|---|---|
| Repominify | Builds a knowledge graph (GraphRAG) on top of repomix output — better structural understanding, fewer tokens | Worth evaluating for v2 |
| Code Graph RAG MCP | 5.5x faster than codebase-memory-mcp, 11 languages, 26 query methods | Stronger alternative to codebase-memory-mcp |
| Ollama (local LLM) | Keeps all code on-device — no data leaves the machine | Critical for security-conscious teams |

**Key insight:** Repominify processes repomix output into a richer graph — it is a better replacement for repomix, not for codebase-memory-mcp. These are two different layers. codebase-memory-mcp handles architecture graph and relations; codebase-context handles git patterns and team decisions. Both serve different adapter needs and cannot be collapsed into one without signal loss.

We will feed findings back to Team 1. The tooling question and the competitive research question are the same question from different angles — you can't evaluate the tool stack without knowing what signal the adapters actually need.

---

## Research plan

| Question | Method | Owner | Status |
|---|---|---|---|
| What do devs actually do today? | Desk research + published surveys | Paula | ✅ Findings above |
| Competitive tool mapping | Tool survey, docs review | Stuart + Paula | ✅ Findings above |
| Tooling alternatives | Technical comparison | Paula + Team 1 | ⚠️ Initial findings above — needs Team 1 sync |
| Trust / UX factors | Research + pipeline findings | Paula | ✅ Findings above |