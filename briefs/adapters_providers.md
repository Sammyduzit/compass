# Brief: Adapters & Providers

Your job is to write **Phase 2** — the LLM synthesis layer. This is where `AnalysisContext` signals get turned into actual output files (`rules.yaml`, `summary.md`). One focused LLM call per adapter.

**Prerequisite:** Domain models, foundation files, storage/CLI, and collectors should be substantially done before you start. You depend on `AnalysisContext` being populated and `FileSelector` being available.

---

## What you're building

```
compass/adapters/
├── base.py          ← shared Phase 2 runtime
├── rules.py         ← RulesAdapter → rules.yaml
├── summary.py       ← SummaryAdapter → summary.md
└── orchestrator.py  ← loops through requested adapters

compass/providers/
├── base.py          ← provider selection + shared interface
├── claude.py        ← Claude CLI subprocess wrapper
└── codex.py         ← Codex CLI subprocess wrapper
```

---

## Reference files — read these first

- **`FINAL.md`** → sections "v1 Adapters", "LLM Providers", "Structured Output / Schema Enforcement"
- **`STRUCTURE.md`** → sections `compass/adapters/`, `compass/providers/`
- **`examples/rules.yaml`** — the target output for RulesAdapter
- **`TESTING.md`** → "Unit Test Scope" — `test_rules_adapter.py`, `test_summary_adapter.py`

---

## Part 1 — providers/

Two providers, both wrap a CLI subprocess call. No direct API usage — the LLM runs via the `claude` or `codex` CLI binary.

**`base.py`**
- How do you select which provider to use? (from `CompassConfig.provider`, with fallback to config file)
- There's no provider registry — just a small conditional. What does that look like?
- What is the shared interface? (a method that takes a prompt string and returns a string)
- What should happen on non-zero exit or timeout? (`ProviderError`)

**`claude.py` and `codex.py`**
- How do you invoke each CLI and pass the prompt?
- How do you capture stdout as the response?
- Both must implement the same interface defined in `base.py`

---

## Part 2 — adapters/base.py

The shared Phase 2 runtime. This is not an abstract base class with adapter-specific logic — it provides the **shared mechanics** that all adapters use.

- `run_file_selector(criteria)` — how does it call `FileSelector` with adapter-specific criteria?
- `run_grep_ast(files)` — how do you invoke `grep_ast` as a subprocess and get skeletons back?
- `call_provider(prompt)` — delegates to the active provider. How does it get the provider instance?
- `validate_output(raw, schema)` — validates the raw LLM response. What does the retry flow look like? (parse → validate → 1 retry on failure → `SchemaValidationError`)

**One key rule:** `build_prompt()` is NOT in `base.py`. Each adapter builds its own prompt. Why does this matter?

---

## Part 3 — rules.py (`RulesAdapter`)

Produces `rules.yaml`. Uses the most context of any adapter.

- What context sections does `build_prompt()` assemble? (skeletons + repomix bodies + ast-grep patterns + git signals + docs + centrality)
- How do you invoke `repomix --compress` on the selected files?
- How do you load the correct prompt template? (language-specific — use `prompts/loader.py`)
- The output must match the two-level cluster → rules schema. How do you validate it?

**Think about the prompt assembly order:**
- What context does the LLM need first to understand the codebase?
- How do you embed the output schema in the prompt so the LLM follows it?

---

## Part 4 — summary.py (`SummaryAdapter`)

Produces `summary.md`. Simpler context than RulesAdapter — intentionally.

- What context does `build_prompt()` include? (grep_ast skeletons + git signals only)
- What does it explicitly NOT include? (no repomix, no ast-grep patterns from AnalysisContext, no docs)
- Why? (See FINAL.md → "SummaryAdapter" — this is a deliberate decision, not an omission)
- `summary.md` is Markdown, not YAML. How does validation work differently here?

---

## Part 5 — orchestrator.py

Loops through the adapters requested in `CompassConfig.adapters` and runs each one.

- How do you instantiate the right adapter from a string like `"rules"` or `"summary"`?
- Should adapters run sequentially or concurrently? Why?
- What should happen if one adapter fails — do you abort or continue with the next?

---

## Definition of done

- [ ] Both `claude.py` and `codex.py` wrap their respective CLI calls and return the LLM response as a string
- [ ] `adapters/base.py` provides `run_file_selector()`, `run_grep_ast()`, `call_provider()`, `validate_output()`
- [ ] `RulesAdapter.build_prompt()` includes all context sections listed in FINAL.md
- [ ] `SummaryAdapter.build_prompt()` includes only grep_ast skeletons + git signals
- [ ] Invalid LLM output triggers exactly 1 retry, then raises `SchemaValidationError`
- [ ] `ProviderError` is raised on non-zero CLI exit or timeout
- [ ] `adapters/orchestrator.py` runs only the adapters listed in `CompassConfig.adapters`
