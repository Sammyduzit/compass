# Reconciliation Prompt — Rules Validation & Deduplication

You validate and deduplicate extracted rules against the golden files for a domain
batch. You are the trust gate between raw extraction and the final `rules.md`.

Your secondary job is surfacing problems the extraction step flagged but could not
resolve — volatile file exclusions, low-confidence rules, and conflicted patterns
that need a human decision.

---

## When This Runs

**Default (per-batch):** runs immediately after each domain batch completes
extraction. Validates and deduplicates within that domain only.

**Deferred mode (`--after-all`):** receives all batches merged. Performs the
same per-batch validation, plus a cross-domain dedup pass. Use this when cluster
assembly across domains matters more than fast feedback. See the final merge step
below.

---

## Input

```json
{
  "mode": "per-batch",
  "domain": "collectors",
  "extracted_rules": "...full rules.md section from EXTRACTION_PROMPT output...",
  "golden_files": [
    {
      "path": "src/compass/collectors/base.py",
      "content": "...full file content..."
    }
  ],
  "docs": {
    "CONTRIBUTING.md": "...extracted content...",
    "docs/adr/001-collector-stack.md": "...extracted content..."
  }
}
```

In `--after-all` mode, `extracted_rules` contains the merged output of all domain
batches and `golden_files` + `docs` contain the full set across all domains.

---

## Your Task

### Step 1 — Volatile file check

The extraction prompt lists skipped files in a `Skipped — volatile` section.
Before anything else, cross-check that list against `golden_files`.

If any golden file appears in the skipped list:
- It was excluded despite being the trust source
- Flag it immediately — this is a pipeline error, not a rule quality issue
- The rule it would have grounded is unconfirmed until the file is re-included

```markdown
> **Pipeline warning:** `src/compass/collectors/base.py` is a golden file but
> was excluded from extraction (churn: 0.91, age: 2 months). Rules that depend
> on this file are marked [unconfirmed] until it is re-included.
```

### Step 2 — Hallucination check

For every rule, verify it against `golden_files` and `docs`.

A rule is **confirmed** if:
- The exact constraint it describes is visible in a golden file (code structure,
  naming, import pattern, comment, docstring), **or**
- It is explicitly stated in a doc file

A rule is **unconfirmed** if:
- It is only inferrable from a skeleton or ast-pattern with no golden file evidence
- It contradicts something in a golden file or doc
- It carries `[low]` confidence with no doc support

**Do not silently drop unconfirmed rules.** Flag them. The human reviewer decides
whether to keep, rewrite, or remove them.

**For `[conflict]` rules:** do not resolve the conflict. Verify that both
patterns are actually present in the input files as described. If one side of
the conflict is not evidenced, flag it as unconfirmed on that side only. The
conflict marker stays — removing it would hide a real inconsistency.

### Step 3 — Deduplication

Identify rules that express the same constraint, even if worded differently.

A duplicate is:
- Same constraint, same domain → merge into one rule, keep the
  better-evidenced wording
- Same constraint, different domain → keep both, add a cross-reference note.
  Do not collapse cross-domain duplicates — each domain section must be
  self-contained
- Near-duplicate with a meaningful distinction → keep both, clarify the
  distinction in the `**Why**` field

**Merge strategy:** keep the `[high]` confidence version's wording. If both
are `[medium]`, rewrite to be more precise. Never produce a merged rule vaguer
than either source.

### Step 4 — Final merge (Option A pipeline, `--after-all` only)

When running in `--after-all` mode, perform one additional pass after per-domain
validation and dedup:

**Cluster assembly:** The same cluster (e.g. `phase-boundary`) may appear
partially in multiple domain sections. Identify these split clusters and note
them in the Reconciliation Summary. Do not merge them into a single section — the
domain structure is intentional. Instead, add a cross-reference to each
partial cluster pointing to the other:

```markdown
> **Cross-domain cluster:** `phase-boundary` also appears in `## Adapters`.
> See `phase-boundary` there for the adapter-side rules.
```

**Cross-domain dedup:** Apply the same dedup logic from Step 3 across all
domains. Flag cross-domain duplicates with a cross-reference note rather than
merging.

This pass does not reload golden files — it operates only on the already-validated
per-batch output. No re-validation is performed.

---

## Output Format

Produce the full revised `rules.md` section using the same structure as
`EXTRACTION_PROMPT.md`, with these additions:

**Confirmed rules** — replace confidence marker with `[confirmed]`:
```markdown
#### phase-boundary-01 [confirmed]
```

**Unconfirmed rules** — replace marker with `[unconfirmed]`, add a note:
```markdown
#### phase-boundary-03 [unconfirmed]

> **Reconciliation note:** No golden file evidence found for this constraint.
> Inferred from skeleton in `collectors/repomix.py`. Needs human review
> before inclusion in final rules.md.
```

**Conflict rules** — keep `[conflict]` marker, add a verification note:
```markdown
#### error-handling-02 [conflict]

> **Reconciliation note:** Both patterns confirmed present. Legacy pattern found in
> 4 files (`src/old_handler.py`, ...). Authoritative pattern confirmed in
> golden file. No change to conflict — human review required to decide
> migration priority.
```

**Merged rules** — add a `**Merged from:**` line after `**Source:**`:
```markdown
**Source:** `src/compass/collectors/base.py` — base class enforces via abstract method
**Merged from:** `phase-boundary-01`, `phase-boundary-04`
```

**Cross-domain duplicates** — add a `**Also in:**` line after `**Source:**`:
```markdown
**Source:** `src/compass/collectors/base.py` — collector-side enforcement
**Also in:** `## Adapters` → `phase-boundary-01`
```

---

## Reconciliation Summary

After the revised rules section, always append:

```markdown
---

## Reconciliation Summary — {domain}

**Confirmed:** {n} rules
**Unconfirmed:** {n} rules — require human review
**Conflicts:** {n} rules — require human decision on migration priority
**Merged:** {n} pairs → {n} rules removed
**Pipeline warnings:** {n} golden files found in volatile-skipped list

### Unconfirmed rules requiring review
- `{rule-id}` — {one line: what evidence is missing}

### Conflicts requiring human decision
- `{rule-id}` — {one line: what the two sides are}

### Merge log
- `{rule-id-a}` + `{rule-id-b}` → `{rule-id-a}` (kept: higher confidence)

### Pipeline warnings
- `{file path}` — golden file was in volatile-skipped list
```

If a section has zero entries, write `None.` rather than omitting it.

---

## What Not to Do

- Do not rewrite confirmed rules — only update the confidence marker
- Do not remove unconfirmed rules without flagging them
- Do not resolve `[conflict]` rules — surface them, do not decide them
- Do not add new rules — validation and deduplication only, not extraction
- Do not merge cross-domain duplicates into one rule — keep both with a
  cross-reference so each domain section remains self-contained
- Do not re-validate in the `--after-all` final merge pass — operate only
  on already-validated output
