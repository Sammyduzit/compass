### 1. Triage summary

Nine violations across all four files. The most critical is in `repomix_collector.py`, which breaks both the phase boundary and the no-API-key guarantee in the same block of code — a collector that calls the Anthropic SDK directly undermines the entire architecture. Fix that file first, then `rules_adapter.py` (two high-severity adapter violations), then `analysis_context.py` (broken staleness logic), and finally `cli.py`.

---

### 2. Violations — ordered by severity

---

**Critical** `phase-boundaries / pb-01` + `llm-integration / llm-01` — collector calls LLM via direct Anthropic SDK

**Consequence:** Phase 1 is no longer zero-LLM-cost; every collection run incurs API charges and requires a secret key, breaking the subscription-only distribution model.

```python
# ❌ current — repomix_collector.py
import anthropic
client = anthropic.Anthropic()

class RepomixCollector:
    def collect(self, repo_path: str) -> dict:
        result = subprocess.run(["repomix", "--compress", str(repo_path)], ...)
        raw = result.stdout
        summary = client.messages.create(...)   # LLM call in Phase 1
        return {"source": summary.content[0].text}

# ✅ correct — return raw data only; synthesis happens in Phase 2
class RepomixCollector:
    def collect(self, repo_path: str) -> dict:
        result = subprocess.run(
            ["repomix", "--compress", str(repo_path)],
            capture_output=True,
            text=True,
        )
        return {"source": result.stdout}
```

---

**Critical** `phase-boundaries / pb-03` — collector imports LLM package

**Consequence:** Import-time coupling makes the phase boundary invisible; any future developer can accidentally invoke synthesis from a collector without realising they've crossed the boundary.

```python
# ❌ current
import anthropic   # top of repomix_collector.py

# ✅ correct — remove entirely; no LLM imports in any collector file
```

_Fixing `pb-01` and `llm-01` above resolves this as a side-effect._

---

**High** `adapter-interface / ai-01` — `RulesAdapter` does not extend `BaseAdapter`

**Consequence:** The adapter cannot be selected via `--adapters` or re-run independently; the shared interface contract is broken for every downstream consumer.

```python
# ❌ current
class RulesAdapter:
    def run(self, context: dict) -> dict:
        ...

# ✅ correct
class RulesAdapter(BaseAdapter):
    context_sections = ["architecture", "git_patterns", "source"]
    output_schema = RULES_SCHEMA
    prompt_template = "prompts/extract_rules.md"

    def run(self, context: AnalysisContext) -> AdapterOutput:
        ...
```

---

**High** `adapter-interface / ai-02` — `RulesAdapter.run()` makes two LLM calls

**Consequence:** Doubles the cost of every rules-extraction run and breaks the per-adapter budget cap guarantee.

```python
# ❌ current
def run(self, context: dict) -> dict:
    clusters = synthesize(f"Identify clusters from: {context['architecture']}")
    rules = synthesize(f"Extract rules from: {context['source']}")  # second call
    return {"clusters": clusters, "rules": rules}

# ✅ correct — one prompt, one call
def run(self, context: AnalysisContext) -> AdapterOutput:
    prompt = self.build_prompt(context)
    return synthesize(prompt, schema=self.output_schema)
```

---

**High** `analysis-context / ac-03` — hash mismatch silently re-collects instead of warning and exiting

**Consequence:** Users unknowingly incur re-collection cost they didn't request; stale-detection is silently bypassed, making `--reanalyze` meaningless as a control.

```python
# ❌ current
if stored_hash != current_hash:
    from compass.collectors import run_all
    fresh = run_all(repo_path)
    return cls(fresh)

# ✅ correct
if stored_hash != current_hash:
    print("Warning: repo has changed since last analysis. Run with --reanalyze to refresh.")
    sys.exit(1)
```

---

**High** `phase-boundaries / pb-02` — fresh context is not persisted before adapters run

**Consequence:** When re-collection is triggered (e.g. on first run), adapters receive an in-memory context object that was never saved — adapters are no longer independently re-runnable.

This is implicit in `analysis_context.py`'s `load()` and surfaced in `cli.py`. After fixing `ac-03`, ensure the pipeline always persists before any adapter call:

```python
# ✅ correct — in cli.py or the pipeline orchestrator
context = AnalysisContext.load(repo_path)   # loads persisted, verified context
for adapter in adapters:
    adapter.run(context)

# If first run or --reanalyze, collect and save BEFORE adapters:
context = run_all_collectors(repo_path)
context.save(repo_path)   # persisted here
for adapter in adapters:
    adapter.run(AnalysisContext.load(repo_path))
```

---

**Medium** `analysis-context / ac-02` — `repo_hash` is not stored in `analysis_context.json`

**Consequence:** The staleness check in `load()` compares `stored_hash` against `current_hash`, but `stored_hash` will always be `None` — every load appears stale, making `--reanalyze` trigger unconditionally or never correctly.

```python
# ❌ current
output = {
    "collected_at": datetime.utcnow().isoformat(),
    "architecture": self.data.get("architecture"),
    ...
}

# ✅ correct
output = {
    "repo_hash": self.data["repo_hash"],   # must be set during collection
    "collected_at": datetime.utcnow().isoformat(),
    "architecture": self.data.get("architecture"),
    "git_patterns": self.data.get("git_patterns"),
    "source": self.data.get("source"),
}
```

---

**Medium** `python-style / py-02` — interactive `input()` prompt in `cli.py`

**Consequence:** Breaks pipe-based and CI usage; any non-TTY invocation hangs indefinitely.

```python
# ❌ current
answer = input(f"Run analysis on {repo_path}? (y/n): ")
if answer.lower() != "y":
    return

# ✅ correct — remove the prompt entirely; the user invoked the command, that is consent
def main(repo_path, adapters):
    context = AnalysisContext.load(repo_path)
    for adapter in adapters:
        adapter.run(context)
```

---

### 3. What's correct

**`repomix_collector.py`** — The `subprocess.run` invocation for repomix itself is exactly right: correct flags, `capture_output=True`, `text=True`. That pattern should be replicated in all collector subprocess calls.

**`analysis_context.py`** — `_hash_repo` using `git rev-parse HEAD` is a solid staleness signal and the right tool for the job. The `path.parent.mkdir(parents=True, exist_ok=True)` guard before writing is also correct defensive practice for output directories.

**`cli.py`** — The overall orchestration shape (`load → iterate adapters → run`) is architecturally correct and matches the spec. Only the interactive prompt needs to be removed.

---

### 4. Fix checklist

```
[ ] repomix_collector.py — pb-01 + llm-01: remove Anthropic SDK import and LLM call; return raw subprocess output only
[ ] repomix_collector.py — pb-03: remove `import anthropic` (resolved by pb-01 fix)
[ ] rules_adapter.py    — ai-01: extend BaseAdapter; add context_sections, output_schema, prompt_template
[ ] rules_adapter.py    — ai-02: collapse two synthesize() calls into one
[ ] analysis_context.py — ac-03: replace silent re-collection with warning + sys.exit(1) on hash mismatch
[ ] analysis_context.py — pb-02: ensure fresh context is saved before any adapter runs (pipeline orchestrator)
[ ] analysis_context.py — ac-02: write repo_hash into the persisted JSON in save()
[ ] cli.py              — py-02: remove input() prompt; invocation is consent
```
