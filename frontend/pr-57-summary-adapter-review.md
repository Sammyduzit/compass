# PR #57 — SummaryAdapter Review & Fix Log

Branch: `feat/issue-31-summary-adapter` → `dev`

---

## What this PR delivers

SummaryAdapter is the Phase 2 adapter responsible for generating `summary.md` and `summary.json` from a repository's analysis context. It makes a single LLM call and produces two outputs in one pass:

- **`summary.md`** — a human-readable five-section onboarding summary (what it does, where to start, what's stable, what's changing, how it connects)
- **`summary.json`** — a structured version of the same content for the v2 API/UI layer

The adapter sits at the end of the Phase 1 → Phase 2 pipeline:

```
Collectors → analysis_context.json → SummaryAdapter → summary.md + summary.json
```

Context used: grep_ast skeletons + git signals + README (read directly from disk if present). No repomix, no ast-grep, no docs_reader.

---

## Review rounds

### Sammy's Review 1 — all fixed in `9059d12`

| Issue | Fix |
|-------|-----|
| `_JSON_BLOCK` regex not anchored to `## JSON Output` section | Anchored with `re.compile(r'## JSON Output.*?```json\s*(\{.*?\})\s*```', re.DOTALL)` |
| `repo_name` missing from `repo_input` | Added as first field |
| Wrong skeleton function (`run_grep_ast` instead of `render_skeletons`) | Replaced with `render_skeletons(files)` |
| Voice framing block not yet in template | Deferred (handled separately) |

### Sammy's Review 2 — all fixed in `1ce0ac6`

| Issue | Fix |
|-------|-----|
| Top-level `skeletons` key still in `repo_input` (duplicate data) | Removed; skeletons are inline at `files[].skeleton` only |
| `FileSelector` removed — all files sent unfiltered to LLM | Reinstated `select_files(context, SUMMARY_SELECTION_CRITERIA, lang)` |
| `SkeletonError` not caught — adapter crashed with unhandled exception | Wrapped in `try/except`, re-raised as `AdapterError` |
| `self._config.lang` — field existence unverified | Confirmed; `CompassConfig` has `lang: str = 'auto'` |

---

## Independent review fixes — `feat/issue-31-summary-adapter` (post-review)

Seven issues identified and fixed before pushing for re-review.

### H1 — `render_skeletons` called with relative paths (production bug)

**Problem:** Paths stored in `analysis_context.json` are relative (e.g. `"src/app.py"`). `skeleton.py` calls `Path(path).read_text()` with no base directory — resolves against CWD. Works in dev (where you run from the repo), breaks for any normal user invocation.

**Fix:** In `run()`, convert selected files to absolute paths before calling `render_skeletons`, then remap keys back to relative so `build_prompt` stays unchanged:

```python
abs_files = [str(self._paths.target_path / p) for p in selected_files]
abs_skeletons = render_skeletons(abs_files)
skeletons = {str(Path(k).relative_to(self._paths.target_path)): v for k, v in abs_skeletons.items()}
```

### H2 — `read_analysis_context` errors escaped `AdapterError` contract

**Problem:** `read_analysis_context` can raise `FileNotFoundError`, `json.JSONDecodeError`, `ValueError`. The orchestrator only catches `AdapterError` — anything else propagated unhandled.

**Fix:** Wrapped in `try/except`, re-raised as `AdapterError`:

```python
try:
    context = read_analysis_context(self._paths.target_path)
except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
    raise AdapterError(self.name, f'failed to read analysis context: {exc}') from exc
```

### M1 — Template grounding step said "four questions" but listed five

**Problem:** Commit `1b94cbf` added a fifth grounding question (self-documenting vs. inference-only files) but the prose intro wasn't updated.

**Fix:** Changed "four questions" → "five questions" in `summary.md`.

### M2 — Duplicate `**Field definitions:**` heading in template

**Problem:** The `readme` field was added to the Input section (commit `3f4125d`) under its own `**Field definitions:**` block — creating two identical headings. Confusing for the LLM and for humans reading the template.

**Fix:** Merged `readme` into the single field definitions block.

### M3 — FINAL.md not updated to reflect README inclusion

**Problem:** FINAL.md stated SummaryAdapter context is "grep_ast skeletons only." The README read was added later without updating FINAL.md — creating an apparent architecture violation for anyone cross-checking.

**Fix:** Updated FINAL.md to: *"grep_ast skeletons + git signals + README (read directly from disk if present — not via docs_reader)"*

### M4 — `test_build_prompt_excludes_docs` passed vacuously

**Problem:** The test asserted that `context.docs` content wasn't in the prompt — but it was passing because `tmp_path` had no README file, so `_read_readme` returned `None`. The test didn't verify the actual architectural constraint, and there was no test confirming the README *is* included when present.

**Fix:**
- Renamed to `test_build_prompt_excludes_analysis_context_docs` with a comment explaining it tests that `context.docs` (from DocsReaderCollector) is never passed to `build_prompt`
- Added `test_build_prompt_includes_readme_when_present` — creates a `README.md` in `tmp_path` and asserts its content appears in the prompt
- Added `test_run_raises_adapter_error_on_missing_context` — verifies `FileNotFoundError` from `read_analysis_context` surfaces as `AdapterError`

### L1 — `from pathlib import Path` inside method body

**Problem:** `_read_readme` imported `pathlib.Path` inside the method. Inconsistent with every other file in the codebase.

**Fix:** Moved to module-level imports.

---

## Voice framing block — `650e19b`

The prompt template previously had a voice framing block that was reverted. The original version was too narrow — it wrote for a junior developer specifically and offered only one failure-mode example (tone).

The new version reframes the reader as **anyone on day one of this codebase** — graduate or staff engineer, it doesn't matter. The vulnerability (not knowing where anything is) is universal regardless of experience. The voice is a mentor: direct, treats the reader as a professional, gives them a thread to pull.

Three concrete failure modes are named with examples:
- **Hedging** — saying "may potentially be involved" instead of stating what it does
- **Listing instead of orienting** — file inventories aren't orientation
- **Talking down** — explaining what a cluster is instead of what this cluster does

---

## Test summary

| Before | After |
|--------|-------|
| 114 tests | 116 tests |
| 114 passing | 116 passing |

Two new tests added:
- `test_build_prompt_includes_readme_when_present`
- `test_run_raises_adapter_error_on_missing_context`

---

## Files changed (this review cycle)

| File | Changes |
|------|---------|
| `compass/adapters/summary.py` | Absolute paths for skeletons, error wrapping, import cleanup |
| `tests/unit/test_summary_adapter.py` | 2 new tests, 1 renamed, 1 comment clarified |
| `compass/prompts/templates/summary.md` | Voice block, "five questions", merged field definitions |
| `FINAL.md` | SummaryAdapter context definition updated |

---

## Standup summary

> **PR #57 — SummaryAdapter** is ready for re-review.
>
> We addressed all four issues from Sammy's second review — duplicate skeletons key removed, file filtering reinstated, SkeletonError handled, config field verified — and ran an independent review on top of that before pushing.
>
> The independent review caught seven additional issues: a production bug where skeleton rendering would fail for any user not running Compass from inside the target repo (relative path resolution), unhandled errors from `read_analysis_context` that bypassed our `AdapterError` contract, a grounding step in the prompt that said "four questions" but had five, a duplicate section heading in the template, a FINAL.md discrepancy on the README inclusion, a test that was passing vacuously, and a deferred import inside a method body.
>
> All seven are fixed. Two new tests added, 116 passing, ruff clean.
>
> The voice framing block is also back in — rewritten to frame the reader as anyone on day one of the codebase regardless of experience level, with the mentor register we discussed.
>
> Branch is ahead of origin by 3 commits and ready to push when we're happy with it.
