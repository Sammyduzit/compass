# Compass — Current State (v0 / Extraction Pipeline)

> This document describes what exists **right now**: the working v0 extraction pipeline that Compass is built around. It is the foundation from which the Python CLI will be written.

---

## What exists today

A shell-based extraction pipeline that, given any git repo, produces a `rules.yaml` file of coding conventions extracted from the actual code — not documentation.

**One command to run it:**
```bash
./compass /path/to/target-repo
```

This opens a Claude Code session in the target repo with all tools pre-configured. Inside that session, you run `/extract-rules` to execute the pipeline.

---

## How it works (end to end)

### 1. Shell wrapper (`./compass`)

The `compass` script:
- Takes a target repo path as argument
- Writes a `.mcp.json` into the target repo (temporarily) with both MCPs configured
- Copies the `/extract-rules` slash command into the target repo's `.claude/commands/`
- Starts `claude` from inside the target repo (so `codebase-context` sees it as workspace root)
- Restores/cleans up everything on exit

**Why run from inside the target repo?** `codebase-context` has a hardcoded workspace-root restriction — it only accepts paths under the current working directory. Running claude from the target repo solves this without any patching.

### 2. MCP Tools (configured via `.mcp.json`)

Two MCPs are injected into the session:

| MCP | Tool used | What it provides |
|-----|-----------|-----------------|
| `codebase-memory-mcp` | `get_architecture`, `search_graph` | Layers, clusters, node types, golden file discovery |
| `codebase-context` | `get_team_patterns`, `get_style_guide` | Git-extracted gotchas + decisions, library adoption % |

Binary locations (machine-specific, set in shell wrapper):
- `codebase-memory-mcp`: `/Users/sam/.local/bin/codebase-memory-mcp`
- `codebase-context`: `node ./node_modules/codebase-context/dist/index.js`

### 3. `/extract-rules` Slash Command (`.claude/commands/extract-rules.md`)

Five-step pipeline executed by Claude Code:

| Step | Action | Output |
|------|--------|--------|
| 1 | `list_projects` → `get_architecture` | Layer structure, node distribution, cluster hypotheses |
| 2 | `get_team_patterns` | Library adoption, git gotchas, architectural decisions |
| 3 | Golden file selection (15–25 files) | Coverage: ports, DTOs, validation, handlers, tests, DAO |
| 4 | `repomix --compress` on golden files | ~5–7k token compressed source |
| 5 | Claude synthesis | `rules.yaml` |

### 4. Output: `rules.yaml`

Two-level schema:
```yaml
clusters:
  - name: DAO Adapter Pattern
    context: "Why this cluster exists..."
    golden_file: src/dao/resource-dao-adapter.ts
    rules:
      - id: dao-01
        rule: "Error handling always in the adapter, never in use cases"
        why: "Centralisation — use cases stay DB-ignorant"
        example: |
          # ✅ correct
          ...
```

See `examples/rules.yaml` for a real output from the `layered-command-service` repo.

---

## Prerequisites (manual, for now)

These must be installed on the machine before running:

1. **Claude Code CLI** — `claude` must be in PATH
2. **codebase-memory-mcp** — binary at `~/.local/bin/codebase-memory-mcp` (or in PATH)
3. **repomix** — `npm install -g repomix`
4. **codebase-context** — `npm install` in this repo (installs to `node_modules/`)
5. **Target repo must be indexed** — run `index_repository` inside codebase-memory-mcp before the first run against a new repo

> **Note for v1 Python CLI:** Prerequisites auto-check + setup is a planned feature (see VISIONS.md).

---

## Known quality gaps (from first pipeline run)

From testing against `layered-command-service`:

| Area | Status |
|------|--------|
| Structural patterns | ✓ correct |
| Git gotchas | ✓ correct |
| Layer boundaries | ✓ correct |
| Zod-specific rules | ✗ missed (golden file gap) |
| `it.failing()` test pattern | ✗ missed |
| Hallucinated rule | ✗ one hallucination caught and fixed |

**Root cause:** DTOs, validation, and test files were underrepresented in golden file selection. The `/extract-rules` command now has explicit coverage requirements for all file categories.

---

## What this is NOT yet

- Not a Python CLI
- Not automated (still requires a Claude Code session + manual `/extract-rules` run)
- No `AnalysisContext` persistence
- No prerequisite auto-check
- No `SummaryAdapter`, `DocsAdapter`, or `SkillAdapter`

All of the above is the **v1 Python build** described in `VISIONS.md`.
