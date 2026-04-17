# Compass — Project Rules

Project-specific rules for **Compass**, a CLI pipeline tool that scans codebases
and produces structured artifacts (`rules.yaml`, `summary.md`). These rules take
precedence over the core rules in `PROMPT.md` where they conflict.

---

## Architecture — Phase Boundary (Priority 1)

The pipeline has two strict phases that must never mix:
```
Collectors (no LLM) → AnalysisContext (persisted JSON) → Adapters (one LLM call each)
```

- Collectors must never import or call LLM, provider, or adapter code
- `subprocess.run(["claude", ...])` may only appear inside `providers/`
- Phase 1 must complete and persist `AnalysisContext` before any adapter runs
- Adapters must read from the persisted context — never receive live collector output

```python
# correct — collector returns raw data only
class RepomixCollector:
    def collect(self, repo_path: str) -> dict:
        result = subprocess.run(["repomix", "--compress", repo_path], ...)
        return {"source": result.stdout}

# wrong — collector calling LLM
class RepomixCollector:
    def collect(self, repo_path: str) -> dict:
        raw = subprocess.run(["repomix", ...], ...)
        summary = synthesize(raw)   # NO — Phase 2 territory
        return {"source": summary}
```

```python
# correct — adapter reads persisted context
context = AnalysisContext.load(repo_path)
rules_adapter.run(context)

# wrong — passing live collector output directly to an adapter
raw = collector.collect(repo_path)
rules_adapter.run(raw)   # adapter depends on collector being present
```

```python
# wrong — in any collector file
from compass.synthesis import synthesize
from compass.adapters.rules import RulesAdapter
```

---

## Architecture — Adapter Contract (Priority 2)

- Every adapter must extend `BaseAdapter` and implement `context_sections`,
  `output_schema`, `prompt_template`, and `run()`
- Each adapter must make exactly one LLM call inside `run()` — never more
- Adapters must declare only the context sections they actually use
- v1 ships exactly two adapters: `RulesAdapter` and `SummaryAdapter`

```python
# correct
class RulesAdapter(BaseAdapter):
    context_sections = ["architecture", "git_patterns", "source"]
    output_schema = RULES_SCHEMA
    prompt_template = "prompts/templates/extract_rules.md"

    def run(self, context: AnalysisContext) -> AdapterOutput:
        ...

# wrong — not extending BaseAdapter
class RulesAdapter:
    def run(self, raw_data):
        ...
```

```python
# correct — one LLM call
def run(self, context: AnalysisContext) -> AdapterOutput:
    prompt = self.build_prompt(context)
    return synthesize(prompt, schema=self.output_schema)

# wrong — two LLM calls in one adapter
def run(self, context: AnalysisContext) -> AdapterOutput:
    clusters = synthesize(cluster_prompt)
    rules = synthesize(rules_prompt)   # second call — split into a separate adapter
```

```python
# correct — SummaryAdapter skips source, saves ~4k tokens per call
class SummaryAdapter(BaseAdapter):
    context_sections = ["architecture", "git_patterns"]

# wrong — loading source even though summary doesn't need raw code
class SummaryAdapter(BaseAdapter):
    context_sections = ["architecture", "git_patterns", "source"]
```

```python
# wrong — adding adapters not in v1 scope
from compass.adapters.docs import DocsAdapter   # future, not v1
```

---

## Architecture — LLM Integration (Priority 3)

- LLM calls must use `subprocess.run()` against the CLI — never import the
  Anthropic SDK or call the API directly
- Structured output must use the `--json-schema` flag — never parse LLM output
  manually
- All provider logic must live in `providers/` — never inline CLI calls in adapters
- Budget cap must be passed through as `--max-budget-usd` when configured

```python
# correct
result = subprocess.run(
    ["claude", "--print", "--output-format", "json", prompt],
    capture_output=True,
    text=True,
)

# wrong — direct API call
import anthropic
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
```

```python
# correct — structured output via flag
subprocess.run([
    "claude", "--print",
    "--json-schema", json.dumps(self.output_schema),
    prompt,
], ...)

# wrong — parsing free-form output
raw = subprocess.run(["claude", "--print", prompt], ...)
data = json.loads(raw.stdout)   # will break on malformed output
```

```python
# correct — adapter delegates to provider
from compass.synthesis.providers import synthesize

def run(self, context: AnalysisContext) -> AdapterOutput:
    return synthesize(prompt, provider=self.provider, schema=self.output_schema)

# wrong — inline subprocess call in adapter
def run(self, context: AnalysisContext) -> AdapterOutput:
    result = subprocess.run(["claude", "--print", prompt], ...)
```

```python
# correct — budget cap forwarded when configured
args = ["claude", "--print", "--json-schema", schema, prompt]
if budget:
    args += ["--max-budget-usd", str(budget)]
subprocess.run(args, ...)
```

---

## Architecture — AnalysisContext (Priority 4)

- Must be persisted to `target-repo/.compass/analysis_context.json` after Phase 1
- Must store a hash of the repo state alongside the collected data
- On hash mismatch: warn the user and require `--reanalyze` — never silently
  re-collect or silently serve stale data

```python
# correct
context.save(repo_path / ".compass" / "analysis_context.json")

# wrong — holding context only in memory
context = collectors.run(repo_path)
adapter.run(context)   # re-collection required every time
```

```json
// correct — hash stored alongside collected data
{
  "repo_hash": "abc123...",
  "collected_at": "2026-04-16T10:00:00Z",
  "architecture": {},
  "git_patterns": {},
  "source": "..."
}

// wrong — no hash
{
  "architecture": {},
  "git_patterns": {}
}
```

```python
# correct — user is in control
if stored_hash != current_hash:
    print("Warning: repo has changed since last analysis. Run with --reanalyze to refresh.")
    sys.exit(1)

# wrong — silently re-collecting
if stored_hash != current_hash:
    context = collectors.run(repo_path)   # user didn't ask for this
```

---

## Project Structure

```
src/compass/
├── domain/        ← Data structures only. One file per model. No CLI or provider logic.
├── collectors/    ← Phase 1. No LLM calls. Produces AnalysisContext.
├── adapters/      ← Phase 2. One LLM call each. Consumes AnalysisContext.
├── providers/     ← Subprocess wrappers only. No business logic.
├── prompts/
│   └── templates/ ← Standalone .md files. No inline prompt strings in Python.
├── schemas/       ← Output validation per adapter.
├── storage/       ← Persistence: analysis_context.json, repo_state.json, output files.
└── utils/         ← Low-level helpers only. If logic is domain-specific, move it out.
```

- Module names must describe one concrete responsibility — no `models.py`,
  `helpers.py`, `registry.py`
- One file per domain model — no generic containers for unrelated data classes
- Do not shadow stdlib modules — use `log.py`, not `logging.py`
- Do not introduce `services/`, `managers/`, `engine/`, `core/`, or registries for
  single-implementation cases
- `domain/` must remain independent from CLI and provider logic
- `storage/` owns all filesystem persistence — collectors and adapters must not
  write files directly
- Prompt templates must be standalone `.md` files in `prompts/templates/` — never
  inline strings in Python
- All output must be written to `target-repo/.compass/output/` — never into the
  Compass source tree

```python
# correct
output_path = repo_path / ".compass" / "output" / "rules.yaml"

# wrong — writing into Compass's own source tree
output_path = Path(__file__).parent / "output" / "rules.yaml"
```

---

## Output Conventions

`rules.yaml` must follow the locked two-level schema:
Cluster (`name`, `context`, `golden_file`) → Rules (`id`, `rule`, `why`, `example`)

```yaml
# correct
clusters:
  - name: Error Handling
    context: "..."
    golden_file: src/lib/attempt-result.types.ts
    rules:
      - id: err-01
        rule: "..."
        why: "..."
        example: "..."

# wrong — flattened or missing fields
rules:
  - id: err-01
    rule: "..."
```

`analysis_context.json` and `output/` must be added to the target repo's
`.gitignore` — never committed.

---

## Python-specific Constraints

- v1 must be Python only — no shell scripts, Node scripts, or Go binaries
- Compass must be non-interactive — no `input()` mid-run. All config via CLI flags
- Distribution is `git clone` + `pip install -e .` only — no PyPI publishing
- Compass must not write or scaffold code in the target repo — only `.compass/`
  artifacts
- Do not add optional features or speculative adapters outside `DECIDED.md` scope

```python
# wrong — prompting the user mid-run
answer = input("Re-analyze? (y/n): ")

# correct — require explicit flag
if args.reanalyze:
    context = collectors.run(repo_path)
```

```python
# wrong — writing source files into target repo
(repo_path / "src" / "generated_types.ts").write_text(...)

# correct — only writing to .compass/
(repo_path / ".compass" / "output" / "rules.yaml").write_text(...)
```
