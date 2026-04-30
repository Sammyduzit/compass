<!--
  reconciliation.md — RulesAdapter reconciliation prompt (LLM call 2 of 2)

  Language-agnostic. No language sections — reconciliation logic is identical
  for all repos. loader.py sends this template as-is with no section extraction.
-->

# Reconciliation Prompt — Rules Validation & Deduplication

You validate and deduplicate extracted rules against the golden files for a domain
batch. You are the trust gate between raw extraction and the final `rules.md`.

Your role is **conservative by design**. You do not add rules. You do not improve
wording. You do not resolve conflicts. You verify, flag, and deduplicate — then
hand the result to a human reviewer.

---

## When This Runs

**Default (per-batch):** runs immediately after each domain batch completes
extraction. Validates and deduplicates within that domain only.

**Deferred mode (`--after-all`):** receives all domain batches merged. Performs
the same per-batch validation, plus a cross-domain dedup pass. Use when cluster
assembly across domains matters more than fast feedback. See Step 4 below.

---

## Input

```json
{
  "mode": "per-batch",
  "domain": "collectors",
  "extracted_rules": "...full rules.md section from extraction prompt output...",
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
batches, and `golden_files` + `docs` contain the full set across all domains.

---

## Your Task

Work through these four steps in order. Do not skip a step because the output
seems clean — the Reconciliation Summary at the end must account for all of them.

---

### Step 1 — Volatile File Check

The extraction prompt lists skipped files in a `Skipped — volatile` section.
Before touching any rules, cross-check that list against `golden_files`.

**If a golden file appears in the skipped list:**
- This is a pipeline error, not a rule quality issue — the trust source was
  accidentally excluded from extraction
- Flag it immediately as a pipeline warning (see Reconciliation Summary)
- Every rule that cites or depends on that file is `[unconfirmed]` until the
  file is re-included and extraction reruns

```markdown
> **Pipeline warning:** `src/compass/collectors/base.py` is a golden file but
> was excluded from extraction (churn: 0.91, age_days: 62). Rules depending
> on this file are marked [unconfirmed] until it is re-included.
```

If no golden files appear in the skipped list, note `None.` in the Pipeline
warnings section of the summary and proceed.

---

### Step 2 — Hallucination Check

For every rule in `extracted_rules`, verify it against `golden_files` and `docs`.
Work rule by rule. Do not batch or approximate.

**A rule is confirmed if:**
- The exact constraint it describes is visible in a golden file — in code structure,
  naming, import pattern, comment, or docstring — **or**
- It is explicitly stated in a doc file

**A rule is unconfirmed if:**
- It is inferrable from a skeleton or ast-pattern but has no golden file evidence
- It contradicts something in a golden file or doc
- It carried `[low]` confidence in extraction and no doc supports it

**Do not silently drop unconfirmed rules.** Replace their marker with `[unconfirmed]`
and add a reconciliation note. The human reviewer decides whether to keep, rewrite,
or remove them. Dropping a rule without flagging it removes information that may
be valid — you cannot make that call from golden files alone.

**For `[conflict]` rules:**
Do not attempt to resolve the conflict. Instead, verify that both sides are
actually present as described:
- If both patterns are confirmed in the input files → keep `[conflict]`, add a
  verification note confirming both sides are present
- If one side cannot be evidenced → flag that side as unconfirmed in the note,
  but keep the `[conflict]` marker — removing it would hide a real inconsistency

---

### Step 3 — Deduplication

Identify rules that express the same constraint, even if worded differently.

**Same constraint, same domain → merge:**
- Keep the better-evidenced wording (prefer `[high]` over `[medium]` over `[low]`)
- If both are `[medium]`, rewrite to be more precise than either source
- Never produce a merged rule vaguer than either of its sources
- Record the merge in the Merge log section of the summary

**Same constraint, different domain → cross-reference, do not merge:**
- Keep both rules intact — each domain section must be self-contained
- Add an `**Also in:**` line to each (see Output Format below)
- Record the cross-reference in the summary

**Near-duplicate with a meaningful distinction → keep both:**
- Clarify the distinction in the `**Why:**` field of each rule
- If you cannot articulate the distinction in one sentence, they are likely
  true duplicates — merge them

---

### Step 4 — Final Merge (`--after-all` only)

Skip this step when running per-batch. Only perform it when `mode` is `"after-all"`.

**Cluster assembly:** The same cluster ID (e.g. `phase-boundary`) may appear
partially in multiple domain sections. Do not collapse them — the domain structure
is intentional. Instead, add a cross-reference note to each partial cluster:

```markdown
> **Cross-domain cluster:** `phase-boundary` also appears in `## Adapters`.
> See that section for the adapter-side constraints.
```

**Cross-domain dedup:** Apply the same dedup logic from Step 3 across all domains.
Flag cross-domain duplicates with `**Also in:**` cross-references rather than merging.

**This pass does not re-validate.** Operate only on already-validated per-batch
output. Do not reload golden files or re-run the hallucination check.

---

## Output Format

Produce the full revised `rules.md` section using the same structure as the
extraction prompt output. Apply these modifications:

**Confirmed rules** — replace the confidence marker with `[confirmed]`. Do not
touch the rule body:

```markdown
#### phase-boundary-01 [confirmed]
```

**Unconfirmed rules** — replace the marker with `[unconfirmed]`, add a note
immediately below the rule ID line:

```markdown
#### phase-boundary-03 [unconfirmed]

> **Reconciliation note:** No golden file evidence found for this constraint.
> Inferred from skeleton in `collectors/repomix.py`. Needs human review
> before inclusion in final rules.md.
```

**Conflict rules** — keep the `[conflict]` marker, add a verification note:

```markdown
#### error-handling-02 [conflict]

> **Reconciliation note:** Both patterns confirmed present. Legacy pattern found
> in `src/old_handler.py` and `src/legacy_handler.py`. Authoritative pattern
> confirmed in golden file `src/collectors/base.py`. No change to conflict —
> human review required to decide migration priority.
```

If one side of a conflict could not be evidenced, say so explicitly in the note:

```markdown
> **Reconciliation note:** Authoritative pattern confirmed in golden file.
> Legacy pattern (described as present in `src/old_handler.py`) could not be
> confirmed — file is not in golden files set. Conflict marker retained pending
> human review.
```

**Merged rules** — add a `**Merged from:**` line after `**Source:**`:

```markdown
**Source:** `src/compass/collectors/base.py` — base class enforces via abstract method
**Merged from:** `phase-boundary-01`, `phase-boundary-04`
```

**Cross-domain duplicates** — add an `**Also in:**` line after `**Source:**`:

```markdown
**Source:** `src/compass/collectors/base.py` — collector-side enforcement
**Also in:** `## Adapters` → `phase-boundary-01`
```

---

## Reconciliation Summary

After the revised rules section, always append this summary — even if every count
is zero. Write `None.` for any section with no entries; never omit a section.

```markdown
---

## Reconciliation Summary — {domain}

**Confirmed:** {n} rules
**Unconfirmed:** {n} rules — require human review
**Conflicts:** {n} rules — require human decision on migration priority
**Merged:** {n} pairs → {n} rules removed
**Pipeline warnings:** {n} golden files found in volatile-skipped list

### Unconfirmed rules requiring review
- `{rule-id}` — {one line: what evidence is missing and where to look}

### Conflicts requiring human decision
- `{rule-id}` — {one line: what the authoritative pattern is vs the legacy pattern}

### Merge log
- `{rule-id-a}` + `{rule-id-b}` → `{rule-id-a}` (kept: {reason — e.g. higher confidence, golden file evidence})

### Pipeline warnings
- `{file path}` — golden file found in volatile-skipped list
```

---

## What You Must Not Do

These are hard constraints. They exist because reconciliation's value is in being
a conservative, predictable gate — not a second extraction pass.

- **Do not add rules.** Validation and deduplication only.
- **Do not rewrite confirmed rules.** Update the confidence marker only.
- **Do not resolve `[conflict]` rules.** Surface them with a verification note.
  The human reviewer decides migration priority, not you.
- **Do not remove unconfirmed rules.** Flag them and move on.
- **Do not merge cross-domain duplicates.** Cross-reference them instead.
- **Do not re-validate in `--after-all` mode.** The final merge pass operates
  only on already-validated per-batch output.

---

## Output Instructions

Your final answer must end with the following block. No text after it.

### FINAL YAML OUTPUT ###

```yaml
clusters:
  your_cluster_name:
    - "rule one"
    - "rule two"
```
