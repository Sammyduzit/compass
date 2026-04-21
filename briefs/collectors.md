# Brief: Collectors

Your job is to write **Phase 1** — the four collectors that gather raw signals from the target repo and produce the `AnalysisContext`. No LLM involved here. Pure data gathering.

All collectors are `async`. The Runner is fully async. This is a firm design decision — do not work around it.

**Prerequisite:** The domain models (`compass/domain/`) must be finished before you start. You'll be populating those models.

---

## What you're building

```
compass/collectors/
├── base.py          ← async abstract base class
├── import_graph.py  ← codebase-memory-mcp via MCP Python SDK
├── ast_grep.py      ← ast-grep CLI wrapper
├── git_log.py       ← git log parser
├── docs_reader.py   ← reads CONTRIBUTING.md, ADRs, etc.
└── orchestrator.py  ← runs all 4, assembles + persists AnalysisContext
```

---

## Reference files — read these first

- **`FINAL.md`** → sections "Collector Stack", "Import Graph", "AnalysisContext — v1 sections"
- **`STRUCTURE.md`** → section `compass/collectors/`
- **`examples/analysis_context.json`** — what the final output should look like

---

## Part 1 — base.py

Every collector inherits from this.

- What is the minimum interface a collector must implement?
- The base class must be `async` — what does that mean for the `collect()` method signature?
- What should the return type be? (hint: look at what each collector produces and what `AnalysisContext` sections exist)
- Should the base class handle errors, or leave that to each collector?

---

## Part 2 — import_graph.py (`ImportGraphCollector`)

This is the most complex collector. It communicates with the `codebase-memory-mcp` binary via the **official MCP Python SDK** (`pip install mcp`) using JSON-RPC over stdio.

- How do you start a subprocess and communicate with it using the MCP Python SDK?
- What do you ask the MCP binary for? (centrality scores + Louvain cluster assignments)
- What does the response look like, and how do you map it to `FileScore.centrality` and `FileScore.cluster_id`?
- How do you build the `clusters` list `[{id, files}]` for `ArchitectureSnapshot`?
- What should happen if the binary is not installed or crashes? (hint: `CollectorError`)
- The MCP binary needs to be indexed on first run — how do you handle that?

---

## Part 3 — ast_grep.py (`AstGrepCollector`)

Wraps the `ast-grep` CLI (installed via brew/cargo). Extracts structural patterns into the `patterns` section of `AnalysisContext`.

- What patterns are you looking for? (error handling, decorators, naming — see FINAL.md)
- How do you invoke `ast-grep` as a subprocess and capture its output?
- What does the output look like, and how do you store it in `AnalysisContext.patterns`?
- `ast-grep` always runs in Phase 1, but its output is only used by RulesAdapter. Does that change how you implement the collector? (It shouldn't — just produce the data.)
- What should happen if `ast-grep` is not installed?

---

## Part 4 — git_log.py (`GitLogCollector`)

A pure Python parser. No external binary beyond `git` itself.

- What `git log` command gives you the data you need?
- How do you compute a **churn score** per file? (number of times a file was touched)
- How do you compute **logical coupling pairs**? (files that are frequently committed together — code-maat methodology)
- How do you compute **code age** per file? (last modified date)
- What does the output look like in `AnalysisContext.git_patterns` and `AnalysisContext.architecture.file_scores`?
- What should happen if the target path is not a git repo?

---

## Part 5 — docs_reader.py (`DocsReaderCollector`)

Reads documentation files from the target repo.

- Which files do you look for? (CONTRIBUTING.md, ADRs in `docs/adr/`, `.cursor/rules`, README at root only)
- How do you handle the case where none of these files exist?
- The output goes into `AnalysisContext.docs` as a dict — what are the keys and values?
- Like `AstGrepCollector`, this always runs in Phase 1 even for summary-only runs.

---

## Part 6 — orchestrator.py

Runs all 4 collectors, assembles the result, and persists it.

- How do you run all 4 collectors? Should they run concurrently or sequentially?
- How do you assemble the individual outputs into a single `AnalysisContext`?
- Where does it persist the result? (hint: it delegates to `storage/analysis_context_store.py` — that's another team's module, code against the interface)
- What should happen if one collector fails — do you abort everything or continue?

---

## Testing

Write unit tests in `tests/unit/` for each collector. Mock all external binaries — read TESTING.md → "Mock Boundaries" for the full list.

What to cover per collector:
- Happy path: mock returns valid data → correct `AnalysisContext` section produced
- Failure path: mock raises an error → `CollectorError` raised with a useful message
- `orchestrator.py`: all 4 collectors called; one failure aborts correctly

For `ImportGraphCollector` specifically: mock the MCP subprocess entirely — do not test the binary protocol here.

---

## Definition of done

- [ ] All 4 collectors are `async` and inherit from `base.py`
- [ ] `orchestrator.py` runs all collectors and writes `analysis_context.json`
- [ ] `ImportGraphCollector` communicates with the MCP binary via the MCP Python SDK
- [ ] `GitLogCollector` produces churn scores, coupling pairs, and code age
- [ ] All collector failures raise `CollectorError` (from `compass/errors.py`)
- [ ] Unit tests written for all 4 collectors — happy path + failure path
- [ ] All external binaries mocked in unit tests (no real subprocess calls)
