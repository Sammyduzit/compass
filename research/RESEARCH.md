# Onboring — Competitive Research

> **Owners:** Stu + Paula
> **Status:** In progress — framework complete, findings to follow
> **Feeds into:** DECIDED.md (tooling decisions), BRAINSTORM.md (open questions)

---

## The problem we're actually solving

Most onboarding tools are built around one user: the new person who needs to learn.

We think the real problem has two users and two costs:

**The business cost** — onboarding a junior or intern can take six months. That's not just their time. It's senior dev hours interrupted, mistakes made while still learning the rules, re-work, and a long tail of "quick questions" that aren't quick. Companies are not getting rid of juniors — but they need them productive faster, with less drag on the people around them.

**The human cost** — being new is painful. Impostor syndrome. Not knowing what you don't know. Feeling like you're in everyone's way. Asking questions that feel stupid. The new dev doesn't just need information — they need to feel capable enough to actually do the job.

**Our hypothesis:** existing tools solve the business need (produce a document) but ignore the human need (make the person feel able to act). The gap is designing for both.

---

## Three research questions

### 1. What do people actually do today?

Before tools, map the real workarounds — these are the true competition:

- Reading READMEs that haven't been touched in years
- Asking the one person who "knows everything" (and interrupting them constantly)
- Spending a week clicking around hoping patterns emerge
- Grep-ing for conventions nobody wrote down
- Asking AI assistants point questions with no persistent, shareable output
- Just guessing and breaking things

These behaviours tell us what's actually broken and what any tool needs to replace.

### 2. Where is the competitive gap?

Map existing tools across four axes — automated, code-derived, produces a structured artifact, shareable with the team:

| Tool | Automated | Code-derived | Structured artifact | Shareable |
|---|---|---|---|---|
| Confluence / Notion | ✗ | ✗ | ✓ | ✓ |
| Mintlify | Partial | ✗ | ✓ | ✓ |
| Swimm | ✗ | Partial | ✓ | ✓ |
| Greptile / Cosine | ✓ | ✓ | ✗ chat only | ✗ |
| GitHub Copilot / Cursor | ✓ | ✓ | ✗ ephemeral | ✗ |
| **Onboring** | **✓** | **✓** | **✓** | **✓** |

**Hypothesis:** no current tool does all four. That's the gap Onboring occupies.

**Additional UX gap:** none of these tools are designed around how it *feels* to be new. They produce artifacts for the business. Onboring should be designed for the person holding it.

### 3. What makes a new dev trust the output?

This is the UX question the rest of the team hasn't asked yet. If someone runs Onboring and gets a `rules.yaml` — what makes them actually follow it? What signals "this is real and current" vs "this might be wrong"?

This will directly affect design decisions: output format, whether it cites which files rules were derived from, whether it surfaces confidence or gaps, whether there's an interactive layer on top of the static files.

---

## Tooling question (overlaps with Team 1 — Janis & Martins)

The whiteboard flagged: *"research better alternatives / lower usage"* next to the current ingestion tools. This is in our scope.

**Current ingestion stack:**

| Tool | What it does | Question |
|---|---|---|
| `codebase-memory-mcp` | Architecture graph, relations | Is this the right tool or just the familiar one? |
| `repomix` | Compresses codebase ~4-5k tokens | Are there lighter alternatives with equivalent signal? |
| `codebase-context` | Git history, team patterns | What's the actual cost and where is the waste? |

We will feed findings back to Team 1. The tooling question and the competitive research question are the same question from different angles — you can't evaluate the tool stack without knowing what signal the adapters actually need.

---

## Research plan

| Question | Method | Owner | Target |
|---|---|---|---|
| What do devs actually do today? | Desk research + team interviews | TBD | This week |
| Competitive tool mapping | Tool survey, docs review | Paula + [you] | This week |
| Tooling alternatives | Technical comparison | [you] + Team 1 | This week |
| Trust / UX factors | UX review of existing tools | [you] | Next session |

---


