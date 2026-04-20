# Brief: Domain Models

Your job is to write the **core data structures** that every other part of Compass depends on. These are pure Python dataclasses — no logic, no async, no external dependencies. Get the fields and types right and everything else builds cleanly on top.

This is the first thing that needs to be done. Other teams are waiting on you.

---

## What you're building

```
compass/domain/
├── analysis_context.py
├── file_score.py
├── adapter_output.py
├── architecture_snapshot.py
├── git_patterns_snapshot.py
└── coupling_pair.py
```

---

## Reference files — read these first

- **`FINAL.md`** → section "AnalysisContext — v1 sections" (the JSON shape is the spec)
- **`STRUCTURE.md`** → section `compass/domain/` (table of all models + responsibilities)
- **`examples/analysis_context.json`** — concrete example of what the data looks like at runtime

---

## Questions to work through

**Before writing any code:**
- What does the full `AnalysisContext` JSON look like? (See FINAL.md — the JSON block is the spec)
- Which model is the top-level container? Which ones are nested inside it?
- Draw the relationship: which model holds which other models?

**For each model:**
- What fields does it need? What type is each field?
- Are any fields optional? What's a sensible default?
- Should it be a `@dataclass`? A `@dataclass(frozen=True)`? Why?

**Specific models to think through carefully:**
- `FileScore` — what signals does it carry per file? (churn, age, centrality, cluster_id, coupling_pairs — what type is each?)
- `CouplingPair` — what two things does it connect, and how is the strength represented?
- `ArchitectureSnapshot` — it holds `file_scores`, `coupling_pairs`, and `clusters`. What's the type of `clusters`?

> **Design note — `FileScore.coupling_pairs`:** The example uses `list[str]` (paths of coupled files) as a denormalized convenience so FileSelector can cheaply count coupling partners per file. An alternative is to omit this field entirely and have FileSelector iterate over `ArchitectureSnapshot.coupling_pairs` directly — slightly more computation (O(n) scan) but no duplicated state. Both are valid for v1. Choose whichever feels cleaner to you.
- `AnalysisContext` — how does it hold all four sections (architecture, patterns, git_patterns, docs)?

**Serialization:**
- These models are persisted to JSON and read back. How will you handle serialization/deserialization?
- What happens if a field is a list of dataclasses — does your approach handle nested structures?

**One rule you must follow:**
- No logic goes in `domain/`. No methods beyond `__init__`, no imports from other Compass modules. If you find yourself writing a method that does something, it belongs elsewhere.

---

## Definition of done

- [ ] All 6 files written in `compass/domain/`
- [ ] Every field has an explicit type annotation
- [ ] The structure matches the JSON shape in `FINAL.md` exactly
- [ ] `examples/analysis_context.json` can be deserialized into `AnalysisContext` without errors
- [ ] No imports from other `compass/` modules inside `domain/`
