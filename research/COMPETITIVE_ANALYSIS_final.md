# Compass — Competitive Analysis

> **Team 4** · Stuart McLean, Paula Schweppe · Status: Complete
> Feeds into: DECIDED.md, BRAINSTORM.md

---

## How each tool collects data

| Tool | Collection method | LLM sees | Persisted? | Selection intelligence |
|---|---|---|---|---|
| **Compass** | `grep_ast` (code skeleton) + `ast-grep` (pattern queries) + custom git parser (churn, coupling, age) + `import_graph` (centrality) + `docs_reader` | Scoped file set, signal-selected per task | ✓ `analysis_context.json` | ✓ FileSelector — different files per task |
| Mapstr | repomix — whole repo compressed | Whole repo, one blob | ✗ | ✗ |
| Greptile / Cosine | Vector embeddings of full repo | Nearest-neighbour search results | ✗ per session | Partial — vector similarity only |
| GitHub Copilot / Cursor | Full context window or RAG on open files | Whatever is open / nearest match | ✗ ephemeral | ✗ |
| Swimm | Human-authored — no collection | Human text, linked to code | ✓ in IDE | ✗ — human decides |
| Mintlify | Reads JSDoc / TSDoc comments + OpenAPI specs | What developers wrote in comments | ✓ | ✗ |
| GitLoop | Repo indexing + RAG | Query-matched chunks | ✗ per session | Partial — vector similarity only |
| DocuWriter | Source code + inline comments | Partial source scan | ✗ | ✗ |
| Confluence / Notion | Manual human input | N/A | ✓ manual | ✗ |

---

## Cost / benefit / efficiency

| Tool | Setup cost | Per-run cost | Token efficiency | Ongoing cost |
|---|---|---|---|---|
| **Compass** | `pip install -e .` — no API key needed, uses existing Claude CLI subscription | One LLM call per output file, scoped tokens | High — signal-selected files only | Zero — output lives in repo, readable forever |
| Mapstr | npm install + API key (Claude / OpenAI / Gemini / local model) | One LLM call per run, whole repo, billed per token | Low — full repo regardless of need | Per run — token cost accumulates. Built-in cost tracker per analysis. |
| Greptile | API key required — $0.15/query, $0.45/query with advanced model | Per query | Medium — vector match, may miss structure | $0.15–$0.45 per question asked, every time |
| GitHub Copilot / Cursor | IDE extension | Per session | Low — context window fills with noise | ~$10–19/user/month subscription |
| Swimm | Onboarding + authoring time | Zero (human wrote it) | N/A | $16/seat/month (Teams) · $28/seat/month (Enterprise) + senior authoring time |
| Mintlify | Low | Low | Medium — comments only | Free (hobby) · $250/month (Pro, 5 seats) · ~$600+/month (Enterprise) |
| GitLoop | Low | Per query | Medium | Free + $15/month Premium |
| DocuWriter | Low | Per run | Medium | $10/month (Individual) · $19/user/month (Business) · $39/user/month (Enterprise) |
| Confluence / Notion | Low | Zero (static) | N/A | Per seat subscription + maintenance time |

**Key finding:** Compass is the only tool where the collection phase uses no LLM (zero cost), the output is persisted, and no ongoing subscription is needed to read it. Every other automated tool either sends the whole repo to the LLM, charges per query, or requires a per-seat subscription.

---

## What FileSelector changes

The critical difference in Compass's architecture is not *what* data it collects — it is *how it decides what to send to the LLM*.

**Without selection intelligence (all other automated tools):**
```
repo → compress everything → same blob → LLM
```
The LLM receives noise alongside signal. It cannot distinguish a stable core convention from a one-off script.

**With FileSelector (Compass):**
```
repo → churn + centrality + coupling signals → FileSelector → scoped file set → LLM
```

FileSelector uses three signals from the git history:
- **Churn** — files that rarely change hold stable conventions
- **Centrality** — files imported by many others define the actual patterns used everywhere
- **Logical coupling** — files that always change together reveal hidden dependencies no import statement shows

The LLM receives fewer tokens and higher-quality signal. This is where output quality is determined — not in the prompt.

---

## The conventions gap

| | Extracts team coding rules automatically | Source |
|---|---|---|
| Compass | ✓ | ast-grep pattern queries across repo |
| Mapstr | ✗ | summarises what code does, not how team works |
| Greptile / Cosine | ✗ | chat only, no structured artifact |
| Swimm | Partial — human-authored | requires someone to write the walkthrough |
| All others | ✗ | — |

No tool in the market automatically derives team conventions and outputs them as a structured, citable, versioned artifact. This is Compass's only uncontested position.

---

## Trust: provenance per claim

96% of developers do not fully trust AI-generated output. — [The New Stack](https://thenewstack.io/agentic-ai-verification-impact/)

The only mechanism that builds trust is provenance — every claim traceable to its source. — [MIT ContextCite, 2024](https://news.mit.edu/2024/citation-tool-contextcite-new-approach-trustworthy-ai-generated-content-1209)

| | Provenance per rule | Verify in one click |
|---|---|---|
| Compass | ✓ `golden_file` per rule in `rules.yaml` | ✓ |
| Swimm | ✓ linked to live code | ✓ |
| Greptile | Partial — cites files in chat | ✗ no persistent artifact |
| All others | ✗ | ✗ |

Compass is the only tool where every automatically-derived rule links directly to the file it came from.

---

## Full competitive matrix

| Tool | Automated | Code-derived | Structured artifact | Shareable | Conventions-aware | Cites sources | Signals gaps | Install friction |
|---|---|---|---|---|---|---|---|---|
| Confluence / Notion | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | Low |
| Mintlify | Partial | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | Low |
| Swimm | ✗ | Partial | ✓ | ✓ | Partial | ✓ | ✗ | Medium |
| Greptile / Cosine | ✓ | ✓ | ✗ chat only | ✗ | ✗ | Partial | ✗ | Medium |
| GitHub Copilot / Cursor | ✓ | ✓ | ✗ ephemeral | ✗ | ✗ | ✗ | ✗ | Low |
| GitLoop | ✓ | ✓ | Partial | ✓ | ✗ | TBD | TBD | TBD |
| DocuWriter | ✓ | Partial | ✓ | ✓ | ✗ | TBD | TBD | TBD |
| Mapstr | ✓ | ✓ | Partial | ✓ | ✗ | ✗ | ✗ | Low |
| **Compass** | **✓** | **✓** | **✓** | **✓** | **✓** | **✓ planned** | **✓ planned** | **Low** |

---

## Per-tool breakdown

### Greptile
**What they do:** Index the full repo using vector embeddings, answer questions via chat with file references.
**Pricing:** $0.15/query · $0.45/query with advanced model. Usage-based, no flat rate. — [greptile.com/pricing](https://www.greptile.com/pricing)
**Architecture:** RAG — embeds all files into a vector database, retrieves nearest matches per query, feeds to LLM. Nothing persists between sessions.
**Why it falls short:** no persistent artifact, no shared output, no conventions. Every question costs $0.15. The team cannot share what was learned.

### Mapstr
**What they do:** CLI tool, fully automated. Compresses the whole repo, runs one LLM call, produces a natural-language summary + Mermaid dependency graph + structured JSON.
**Pricing:** API key required — Claude, OpenAI, Gemini, or local model. Billed per token per run. Has built-in cost tracker per analysis. — [github.com/BATAHA22/mapstr](https://github.com/BATAHA22/mapstr)
**Architecture:** single-pass — no file selection, no signal analysis, same blob for every run. Provider-agnostic.
**Why it falls short:** explains what the code does, not how the team works. No conventions layer, no `golden_file`, no rules. Closest technical competitor — confirms the idea is viable but leaves the most important gap open.

### Swimm
**What they do:** developers write walkthroughs manually, link them to live code. When code changes, Swimm flags the doc as outdated.
**Pricing:** $16/seat/month (Teams) · $28/seat/month (Enterprise Starter) · Enterprise custom. — [swimm.io/pricing](https://swimm.io/pricing)
**Architecture:** human-authored + live code sync. No automated extraction.
**Why it falls short:** requires a senior developer to write every walkthrough. Works well for teams that already document. Does nothing for repos where nobody did.

### GitHub Copilot / Cursor
**What they do:** AI assistants inside the IDE. Answer questions about open files, suggest completions, explain code on request.
**Pricing:** Copilot ~$10–19/user/month. Cursor similar.
**Architecture:** full context window of open files + optional RAG over the repo. Everything is session-scoped — nothing persists.
**Why it falls short:** ephemeral by design. No shared output, no versioned artifact, no conventions. What one developer learns, the next has to re-ask.

### Mintlify
**What they do:** generate documentation from JSDoc/TSDoc comments and OpenAPI specs. Produces a hosted docs site.
**Pricing:** Free (hobby, 1 seat) · $250/month (Pro, 5 seats, 250 AI credits) · ~$600+/month (Enterprise). — [mintlify.com/pricing](https://www.mintlify.com/pricing)
**Architecture:** reads comments in code, not the code itself.
**Why it falls short:** only surfaces what someone already documented in comments. Conventions in the code but not in comments — invisible.

### GitLoop
**What they do:** chatbot for your repo — ask questions, generate docs and tests, get answers.
**Pricing:** Free tier · Premium $15/month. — [gitloop.com/pricing](https://www.gitloop.com/pricing)
**Architecture:** repo indexing + RAG. Partial structured output.
**Why it falls short:** chat-based, no conventions extraction, no `golden_file`. No one-time run that produces a permanent artifact.

### DocuWriter
**What they do:** generates documentation from source code and inline comments.
**Pricing:** $10/month (Individual) · $19/user/month (Business) · $39/user/month (Enterprise). — [docuwriter.ai](https://www.docuwriter.ai/)
**Architecture:** source code scan + comment extraction. Partial code derivation.
**Why it falls short:** documents what the code does structurally, not the team's conventions. No rules layer, no git signal analysis.

---

## Conclusion

The market splits into three approaches:

**1. Manual** (Confluence, Notion, Swimm) — accurate, but requires senior time to write and maintain. Scales with headcount. Goes stale.

**2. RAG / chat** (Greptile, Copilot, Cursor, GitLoop) — automated, but produces no persistent artifact. Every answer costs a query. Cannot be shared, versioned, or trusted at the rule level.

**3. Pipeline + artifact** (Mapstr, Compass) — automated, produces something permanent. Mapstr does this for summaries. Compass does it for summaries *and* coding rules.

**The gap Compass occupies:** no other tool in category 3 extracts team conventions, cites their source, or uses selection intelligence to determine which files actually matter. Mapstr is the closest technical competitor and does none of these things.

Compass's collection architecture — signal-based FileSelector, persisted AnalysisContext, zero LLM in Phase 1 — is not an implementation detail. It is the reason the output quality and cost profile are different from everything else in the market.

**The single uncontested position: automatically derived, citable, versioned coding conventions. No tool has this. Compass does.**
