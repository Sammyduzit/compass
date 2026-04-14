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

| Tool | Setup cost | Per-run cost | Token efficiency | Output quality driver | Ongoing cost |
|---|---|---|---|---|---|
| **Compass** | `pip install -e .` | One LLM call per output file, scoped tokens | High — only signal-selected files | FileSelector signal quality | Zero — output lives in repo |
| Mapstr | npm install | One LLM call, whole repo | Low — full repo regardless of need | repomix compression ratio | Zero |
| Greptile / Cosine | API key + integration | Per query | Medium — vector match may miss structure | Embedding quality | Accumulates with usage |
| GitHub Copilot / Cursor | IDE extension | Per session / per query | Low — context window fills with noise | What happens to be open | Subscription |
| Swimm | Onboarding + authoring time | Zero (human wrote it) | N/A | Senior developer accuracy | Ongoing authoring to prevent staleness |
| Mintlify | Low | Low | Medium — comments only | Comment coverage in codebase | Low |
| GitLoop | API integration | Per query | Medium | Embedding quality | Accumulates with usage |
| DocuWriter | Low | Per run | Medium | Comment + source coverage | Low |
| Confluence / Notion | Low | Zero (static) | N/A | Human diligence | Maintenance time |

**Key finding:** Compass is the only tool where the collection phase itself is zero-cost (no LLM), the output is persisted, and file selection is task-specific. Every other automated tool either sends the whole repo to the LLM or relies on vector similarity — neither of which understands *why* a file matters.

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

## Conclusion

The market splits into three approaches:

**1. Manual** (Confluence, Notion, Swimm) — accurate, but requires senior time to write and maintain. Scales with headcount. Goes stale.

**2. RAG / chat** (Greptile, Copilot, Cursor, GitLoop) — automated, but produces no persistent artifact. Every answer costs a query. Cannot be shared, versioned, or trusted at the rule level.

**3. Pipeline + artifact** (Mapstr, Compass) — automated, produces something permanent. Mapstr does this for summaries. Compass does it for summaries *and* coding rules.

**The gap Compass occupies:** no other tool in category 3 extracts team conventions, cites their source, or uses selection intelligence to determine which files actually matter. Mapstr is the closest technical competitor and does none of these things.

Compass's collection architecture — signal-based FileSelector, persisted AnalysisContext, zero LLM in Phase 1 — is not an implementation detail. It is the reason the output quality and cost profile are different from everything else in the market.

**The single uncontested position: automatically derived, citable, versioned coding conventions. No tool has this. Compass does.**
