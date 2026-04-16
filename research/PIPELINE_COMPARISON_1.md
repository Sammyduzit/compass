# Compass — Competitor Pipeline Comparison

> **Team 4**
> **Authors:** Stuart McLean, Paula Schweppe
> **Status:** In progress — sourced from public documentation April 2026
> **Note on methodology:** This comparison is based on public documentation, technical blogs, and official product pages. None of these tools have been hands-on tested. Cells marked TBD require further investigation.
> **Feeds into:** COMPETITIVE_ANALYSIS.md, BRAINSTORM.md

---

## How to read this document

Your lead asked for a comparison of the pipeline steps each competitor uses to achieve their output — not just what they produce, but how they get there. For each tool we map four stages:

1. **Ingest** — how does the tool get the codebase in?
2. **AI processing** — what does it actually do with that data?
3. **Output** — what does a human receive at the end?
4. **Human layer** — how does a person actually interact with the result?

---

## Compass (our tool — for reference)

| Stage | What happens |
|---|---|
| **Ingest** | Phase 1 collectors run with zero LLM cost: `grep_ast` extracts code skeleton, `ast-grep` runs pattern queries, custom git parser extracts churn/coupling/age signals, `import_graph` computes centrality scores, `docs_reader` scrapes existing documentation files |
| **AI processing** | `FileSelector` picks the minimal relevant file set per adapter using git signals + centrality. One focused LLM call per output — RulesAdapter gets low-churn + high-centrality files, SummaryAdapter gets hotspots + centrality, no raw source |
| **Output** | `rules.yaml` — structured clusters of coding conventions, each with id, rule, why, example, and `golden_file` citation. `summary.md` — plain English onboarding overview |
| **Human layer** | Files in `.compass/` folder inside the repo. Planned: local web UI (`--ui` flag) with interactive bento-box layout, clickable rules, source citations |

**Key architectural properties:** Two strict phases — no LLM in Phase 1. AnalysisContext persisted to disk. Each adapter independent and re-runnable. FileSelector gives different files to different adapters.

---

## Swimm

| Stage | What happens |
|---|---|
| **Ingest** | Connects to GitHub/GitLab repo via integration. Runs proprietary static analysis — deterministic code mapping that identifies all relevant flows, logical components, and call trees without LLM involvement. Monitors repo continuously via CI/CD pipeline hook |
| **AI processing** | Three-step process: (1) static analysis maps code structure deterministically, (2) LLM generates explanations grounded in that map — not from raw code, (3) validator checks output against the static analysis to catch hallucinations. Human can also author content and link it to specific code blocks |
| **Output** | Markdown `.md` files stored directly in the repo (versioned with code). Module explanations, flow documentation, code-coupled diagrams. IDE-embedded docs that surface when a developer navigates to related code |
| **Human layer** | VS Code and JetBrains plugins show docs inline as you navigate the code. `/ask Swimm` chat interface answers questions grounded in the codebase. Auto-sync flags when code changes make docs stale |

**Key distinction from Compass:** Swimm's static analysis → LLM → validator pipeline directly addresses hallucinations. Their docs live in the IDE alongside the code, not in a separate UI. But everything still requires a human to trigger or author the walkthrough first — it does not autonomously extract conventions.

*Sources: [swimm.io/how-it-works](https://swimm.io/how-it-works), [Swimm static analysis blog](https://swimm.io/blog/how-swimm-uses-static-analysis-to-generate-quality-code-documentation)*

---

## Greptile

| Stage | What happens |
|---|---|
| **Ingest** | Connects to GitHub/GitLab via OAuth. Indexes entire repository — builds a repository-wide dependency graph of every function, class, file, and their relationships. Indexing takes 10–30 minutes depending on repo size. Graph is updated incrementally on each new commit |
| **AI processing** | On each PR, uses multi-hop investigation — traces dependencies, checks git history, follows leads across files. Does not analyse just the diff but the entire codebase graph. As of v3 (late 2025), uses Claude Agent SDK for autonomous investigation. Learns from developer 👍/👎 reactions over time |
| **Output** | Inline PR comments in GitHub/GitLab with suggested fixes. Mermaid diagrams per PR. Confidence scores per comment. Natural language query API for custom tooling. No persistent structured artifact — everything is per-PR or per-query |
| **Human layer** | Lives entirely inside GitHub/GitLab PR workflow. "Fix in X" button sends issues directly to Claude Code, Cursor, or Codex. No separate UI — the PR is the interface |

**Key distinction from Compass:** Greptile builds the deepest codebase graph of any tool here, but produces no persistent artifact. Every answer costs a query. Nothing is shareable or versioned at the rule level. Designed for PR review, not onboarding.

*Sources: [greptile.com/docs/introduction](https://www.greptile.com/docs/introduction), [Greptile review 2026](https://aicodereview.cc/tool/greptile/)*

---

## Mapstr

| Stage | What happens |
|---|---|
| **Ingest** | CLI tool — runs against any local directory. Uses structural parsing (AST-based) to scan the project. Supports `--no-ai` flag for structural analysis only. Configurable depth for dependency tree traversal |
| **AI processing** | Single LLM call — sends compressed structural analysis to chosen provider (Claude, OpenAI, Gemini, Ollama, Deepseek, Mistral). No file selection intelligence — sends the same representation regardless of what the output needs. Multi-provider by design |
| **Output** | Three files: `summary.md` (natural language overview), a Mermaid dependency graph, and structured JSON. All written to `<project>/mapstr/` folder. Watch mode regenerates on file changes |
| **Human layer** | Files in a folder. No interactive UI. No IDE integration. No citations per claim. Can run as MCP server for AI assistants |

**Key distinction from Compass:** Mapstr is the closest technical comparison — same CLI approach, same one-command philosophy, same output-to-folder pattern. But no FileSelector (same blob for every run), no conventions layer (explains what code does not how the team works), no golden_file citations, no Phase 1/Phase 2 separation.

*Sources: [github.com/BATAHA22/mapstr](https://github.com/BATAHA22/mapstr), [earezki.com Mapstr review](https://earezki.com/ai-news/2026-03-08-ai-cli-that-maps-your-codebase-no-reading-required/)*

---

## Mintlify

| Stage | What happens |
|---|---|
| **Ingest** | Connects to GitHub repo. Agent monitors codebase for changes that require documentation updates. VS Code/JetBrains plugin highlights code for inline doc generation. Also reads OpenAPI specs for API documentation. Does NOT parse the codebase for conventions or patterns — reads what developers write |
| **AI processing** | Autopilot agent detects code changes → identifies what documentation needs updating → generates draft PR with proposed doc updates. AI Assistant uses RAG (not traditional keyword-match but multi-step retrieval) over existing docs to answer questions. Pipeline runs on sandboxed Claude Sonnet agents |
| **Output** | Hosted documentation site. Markdown files versioned in repo. Auto-generated API playground from OpenAPI specs. `llms.txt` and `llms-full.txt` for AI discoverability. MCP server so AI tools can query docs in real time |
| **Human layer** | Beautiful hosted docs site with AI chat assistant embedded. VS Code plugin for inline doc generation. Analytics dashboard showing what users search for and can't find |

**Key distinction from Compass:** Mintlify is a documentation platform, not a codebase analysis tool. It makes existing docs beautiful and AI-queryable, and helps keep them in sync. It does not extract conventions from code — it needs humans to write the source material first. An entirely different problem space.

*Sources: [mintlify.com](https://www.mintlify.com), [Mintlify auto-generate blog](https://www.mintlify.com/blog/auto-generate-docs-from-repos), [Mintlify review Ferndesk](https://ferndesk.com/blog/mintlify-review)*

---

## GitHub Copilot / Cursor

| Stage | What happens |
|---|---|
| **Ingest** | Reads currently open files in the IDE. Optional RAG over the full repo (Copilot Workspace, Cursor's codebase indexing). Context window filled with whatever is open or nearest-match to current cursor position |
| **AI processing** | Real-time LLM call on every keystroke or question. No persistent analysis — each session starts fresh. Cursor indexes the repo into a vector store for semantic search. Copilot uses GitHub's infrastructure for context retrieval |
| **Output** | Inline code completions. Chat answers in the IDE sidebar. No persistent artifact — everything disappears when the session ends |
| **Human layer** | Embedded entirely in the IDE. Zero setup for basic use. The developer asks questions and gets answers, but nothing is saved, shared, or versioned |

**Key distinction from Compass:** Ephemeral by design. No shared output, no versioned artifact, no conventions. What one developer learns in a Copilot session, the next developer has to re-ask. Designed for individual productivity, not team knowledge.

---

## Pipeline comparison at a glance

| | Compass | Swimm | Greptile | Mapstr | Mintlify | Copilot/Cursor |
|---|---|---|---|---|---|---|
| **Ingest method** | Multi-signal collectors (AST + git + imports) | Proprietary static analysis + CI hook | Full repo graph via GitHub API | CLI structural parse | GitHub monitoring + plugin | Open files + optional RAG |
| **LLM in ingest?** | No — Phase 1 is zero LLM cost | No — static analysis first | No — graph built deterministically | No — structural parse first | No — change detection first | Yes — real time |
| **File selection intelligence** | Yes — FileSelector per adapter | Partial — module-based | Yes — full graph traversal | No — same blob always | No — change-triggered | No — open files / nearest match |
| **AI processing model** | One focused call per adapter | Static analysis → LLM → validator | Multi-hop agent investigation | Single LLM call, whole repo | RAG + agentic draft generation | Real-time per query |
| **Hallucination guard** | Prompt-level (grounded in source files) | Validator checks output against static analysis | Learning from 👍/👎 feedback | None documented | Human-in-loop for doc updates | None |
| **Output persisted?** | Yes — `analysis_context.json` + output files | Yes — `.md` files in repo | No — per PR / per query | Yes — files in folder | Yes — hosted docs site | No — ephemeral |
| **Conventions extracted?** | Yes — core purpose | Partial — with human authoring | No — PR review focus | No — structural summary only | No — docs platform | No |
| **Source citations per claim** | Yes — `golden_file` per rule | Yes — linked to code blocks | Partial — cites files in comments | No | Yes — citations in AI chat | No |
| **Human experience** | Planned interactive UI | IDE-embedded, inline | Inside GitHub PR | Files in folder | Hosted docs site + AI chat | IDE sidebar |

---

## What this means for Compass

Three things stand out from this comparison:

**The two-phase architecture is genuinely different.** Every other tool either uses real-time LLM calls (Copilot, Cursor) or a single batch LLM call on the full repo (Mapstr). Only Swimm comes close to a separation between analysis and synthesis — and their approach validates the concept. Compass's Phase 1 / Phase 2 split is architecturally sound and costs less per run than any tool that uses the LLM for ingestion.

**FileSelector has no equivalent.** Every tool sends the same representation to the LLM regardless of what the adapter needs. Compass is the only tool where different tasks get different file sets, selected for different reasons. This is where output quality is determined.

**The conventions gap remains uncontested.** After researching every tool here, none of them automatically extract team coding conventions and output them as a structured, citable, versioned artifact. Swimm comes closest but requires human authoring. This remains Compass's uncontested position.

**The area to watch:** Swimm's static analysis → LLM → validator pipeline is the most sophisticated hallucination guard in the market. Their approach of grounding every AI output in deterministic static analysis before generating, then validating after, is worth understanding in detail before Compass ships its prompt design.
