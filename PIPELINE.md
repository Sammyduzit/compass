# Atomic Ruler — Pipeline Findings & Roadmap

## What Works

- codebase-memory-mcp → architecture, file structure, golden file discovery via `search_graph`
- codebase-context → library adoption counts, git-extracted gotchas and decisions
- repomix --compress → 48 files, ~6.7k tokens for a medium codebase
- Claude `/extract-rules` → correct cluster identification, good `why` explanations, git gotchas captured

## Quality Gap (first run vs. manual docs)

| Area | Status |
|------|--------|
| Structural patterns | ✓ correct |
| Git gotchas | ✓ correct |
| Layer boundaries | ✓ correct |
| Zod-specific rules (strictObject, z.infer) | ✗ missing |
| it.failing() test pattern | ✗ missing |
| validBody at describe scope | ✗ missing |
| Factual error in err-02 example | ✗ wrong |
| Hallucinated rule (test-05 Given/When/Then) | ✗ hallucination |

**Root cause:** DTOs, validation, and test files were underrepresented in golden file selection.

## Fixes Applied to /extract-rules

- Explicit golden file criteria: must include DTOs, validation, and at least one full test pair
- Hallucination guard: derive rules only from observed code, not assumptions
- list_projects before get_architecture to get correct project name

## Rules vs. Templates

`rules.yaml` contains rules + short examples — intentionally no full file templates.

**Why:** Agent skills (review, implement, plan) need rules + short examples to work effectively.
Full templates are too much context per skill and don't compose well.

## Future Pipeline Steps

### `/extract-templates` (planned)
- Separate command, separate output file (`templates.yaml` or `templates/`)
- One template per file-type role (handler, use-case, dtos, validation, test)
- Input: same golden files as `/extract-rules`
- Primary consumer: implementer-agent (scaffolding new features)

### Agent Skills (planned)
- Input: `rules.yaml` clusters
- One skill per cluster, or grouped by agent type
- review-agent: error handling, type safety, layer boundaries, handler pattern
- implementer-agent: factory pattern, mapper pattern, file conventions + templates
- plan-agent: architecture overview, layer boundaries, folder structure
