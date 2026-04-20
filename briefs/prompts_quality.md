# Brief: Prompts & Quality

Your job is to write the **prompt templates** that tell the LLM what to do, and define what **valid output** looks like. This is one of the most important parts of the project — the quality of Compass's output depends directly on your work here.

You work independently. Your deliverables don't depend on other teams finishing first.

---

## What you're building

```
compass/prompts/templates/
├── extract_rules.md     ← RulesAdapter extraction prompt (language-aware sections within)
├── reconciliation.md    ← RulesAdapter reconciliation prompt (language-agnostic)
└── summary.md           ← SummaryAdapter prompt (language-aware sections within)
compass/schemas/              ← 2 schema files (you write these)
examples/                     ← reference outputs (you update these)
```

---

## Reference files — read these first

Before you start, read these files in the repo root:

- **`FINAL.md`** — what each adapter does, what context it receives, what it outputs
- **`examples/rules.yaml`** — the target output format for RulesAdapter
- **`STRUCTURE.md`** → sections `compass/prompts/` and `compass/schemas/`

---

## Part 1 — Prompt Templates

You need to write 3 template files. Language variants (python / typescript / generic) live as clearly labelled sections **within** each template — not as separate files. `prompts/loader.py` extracts the relevant section at runtime based on the detected language.

**`extract_rules.md` — RulesAdapter extraction prompt**

RulesAdapter makes two LLM calls: extraction (this template) and reconciliation (next template). Read `PROMPTS/EXTRACTION_PROMPT.md` in the repo root — this is the reference implementation Janis produced. Study it carefully before writing your version; understand the confidence marker system, conflict detection, and skipped-volatile section.

Work through:
- What is the LLM extracting, and from what input? (code skeletons, ast patterns, git signals, docs, golden files — see FINAL.md)
- How does language (python vs typescript) change what patterns to look for? (decorators, error handling idioms, type system patterns)
- What makes a rule high-confidence vs low-confidence? How does the prompt communicate this?
- What does a `[conflict]` look like, and when should the LLM flag one?

**`reconciliation.md` — RulesAdapter reconciliation prompt**

Runs after extraction. Receives extracted `rules.md` + golden files + docs. Read `PROMPTS/RECONCILIATION_PROMPT.md` as the reference implementation.

Work through:
- What is the reconciliation step validating? (hallucination check, deduplication, volatile file check)
- What does it output? (same `rules.md` structure, with confidence markers updated to `[confirmed]`/`[unconfirmed]`)
- Language is irrelevant here — reconciliation logic is the same for all repos.

**`summary.md` — SummaryAdapter prompt**

Single LLM call. Output is `summary.md` directly — no reconciliation pass.

Work through:
- What is SummaryAdapter trying to produce? (onboarding overview — see FINAL.md)
- What context does it receive? (grep_ast skeletons + git signals only — no repomix bodies, no ast-grep patterns, no docs)
- How does language change what to highlight? (Python: class hierarchy, decorators; TypeScript: interfaces, generics)

---

## Part 2 — Schemas

Two schema files that validate what the LLM returns.

```
schemas/rules_schema.py    ← validates rules.yaml output
schemas/summary_schema.py  ← validates summary.md output
```

Questions to work through:

- What fields are **required** in a valid `rules.yaml`? What's optional?
- What should make validation **fail**? (missing fields, wrong types, empty strings?)
- For `summary.md` — it's Markdown, not YAML. What does "valid" mean here? What's the minimum bar?
- Look at `examples/rules.yaml` — does your schema accept it? It should.

---

## Part 3 — Examples

Update the files in `examples/` so they serve as clear reference outputs.

```
examples/rules.yaml          ← realistic example of RulesAdapter output
examples/summary.md          ← realistic example of SummaryAdapter output
examples/analysis_context.json  ← example of what collectors produce (Phase 1 output)
```

Questions:

- Does `examples/rules.yaml` look like something genuinely useful to a developer onboarding into a new codebase?
- Are the example rules specific enough to be actionable, or are they too generic?
- Does the example follow the schema you defined in Part 2?

---

## Definition of done

- [ ] 3 prompt template files written and in `compass/prompts/templates/`
- [ ] `extract_rules.md` and `summary.md` each have clearly labelled python / typescript / generic sections
- [ ] 2 schema files written and in `compass/schemas/`
- [ ] `examples/rules.yaml` and `examples/summary.md` are realistic and match the schemas
- [ ] Someone unfamiliar with the codebase could read your prompt and immediately understand what the LLM is supposed to do
