# Atomic Ruler — Extract Rules Pipeline

You are running the Atomic Ruler rule extraction pipeline. Your goal is to produce a `rules.yaml` file that captures the coding conventions, architectural patterns, and testing patterns of this repository.

**Critical constraint:** Only derive rules from patterns you can directly observe in the source code or git history. Do not infer, assume, or apply general best practices. If you cannot point to a specific file or commit as evidence, do not write the rule.

Work through the following steps in order. Do not skip steps.

---

## Step 1: Architecture Overview

Call `codebase-memory-mcp → list_projects` first to get the correct project identifier, then call `get_architecture` with that name (not a file path).

From the output, identify:
- The layer structure (folder names, counts)
- The dominant edge types (CALLS, IMPORTS, TESTS_FILE, etc.)
- The node type distribution (Functions, Types, Interfaces, Routes, Classes)

Use this to understand the architecture style (layered, hexagonal, modular, etc.) and to form initial cluster hypotheses.

---

## Step 2: Team Patterns & Git History

Call `codebase-context → get_team_patterns` with `category: "all"` for this repository.

Extract:
- Library usage with adoption counts — these reveal the canonical dependencies
- Git-extracted `gotcha` memories — these reveal past mistakes worth encoding as rules
- Git-extracted `decision` memories — these reveal intentional architectural choices

---

## Step 3: Identify Golden Files

Based on Steps 1 and 2, identify 15–25 "golden files". Use `codebase-memory-mcp → search_graph` to locate them.

**Required coverage — your selection must include at least one file from each of these categories:**
- Ports / interfaces (the domain contracts)
- Shared lib utilities (error types, type guards)
- DI composition root (the wiring file)
- One complete vertical slice for a single resource × operation:
  - DTO schema file (`*.dtos.ts`)
  - Validation file (`*.validation.ts`)
  - Handler file (`*.handler.ts`)
  - Use case file (`*.use-case.ts`)
  - Unit test (`*.handler.test.ts`)
  - Integration test (`*.integration.test.ts`)
- Data store / DAO adapter implementation
- Test utility factories (mock builders, test app factories)

Missing any of these categories will cause gaps in the extracted rules.

---

## Step 4: Run Repomix

Run repomix with `--compress` on the golden files identified in Step 3.

```bash
repomix --compress \
  --include "<comma-separated glob patterns for golden files>" \
  --output /tmp/extract-rules-repomix.xml \
  .
```

Read the output file at `/tmp/extract-rules-repomix.xml`. This is your primary source for pattern extraction.

---

## Step 5: Synthesize rules.yaml

From all data gathered (architecture overview, team patterns, git memories, compressed source), synthesize a `rules.yaml` file.

### Schema

```yaml
clusters:
  - name: <Cluster Name>                  # Pattern group (e.g. "DAO Adapter Pattern")
    context: |                            # WHY this cluster exists, which layer it concerns,
                                          # what problem it solves. 2-4 sentences.
    golden_file: <relative/path.ts>       # Most representative file for this cluster
    rules:
      - id: <cluster-prefix-NN>           # e.g. dao-01, handler-02
        rule: "<Concrete, actionable rule. One sentence.>"  # hard-rule: true if always enforced
        why: "<Why this rule exists — intent, not description.>"
        example: |                        # Required when rule involves non-obvious code shape
          # ✅ correct
          ...
          # ❌ wrong
          ...
```

### Cluster Guidelines

- Aim for 6–10 clusters. Merge closely related rules into one cluster.
- Each rule must be **actionable** — a developer knows exactly what to do and what not to do.
- The `why` field must state **intent or consequence**, not restate the rule.
- Encode `gotcha` memories from git as rules — they represent real mistakes the team made.
- Examples in the `example` field must be derived from actual code in the repomix output — do not write hypothetical examples.
- Mark hard rules (always true, never violated) with `# hard-rule: true` inline.

### Anti-patterns to detect

Look specifically for these common patterns worth encoding:
- Error handling strategy (exceptions vs result types vs try/catch)
- Instantiation pattern (new vs factory functions vs DI containers)
- Type assertion usage (as, any, unknown)
- Validation library and placement (where in the request lifecycle)
- Validation schema style (e.g. strictObject vs object, inferred types vs manual interfaces)
- Layer boundary violations (what can import what)
- Test isolation strategy (what gets mocked, what runs real)
- Test structure conventions (describe/it nesting, shared fixtures, known-failing tests)
- Naming conventions (file names, function names, type names)
- Import conventions (aliases, extensions, relative vs absolute)

---

## Step 6: Output

Write the synthesized `rules.yaml` to the current working directory.

Then provide a brief summary:
- How many clusters and rules were extracted
- Which clusters have the highest confidence (most golden file evidence)
- Any patterns you detected that were ambiguous or had low evidence
