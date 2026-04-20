<!--
  extract_rules.md — RulesAdapter extraction prompt (LLM call 1 of 2)

  Language-aware template. All shared instructions come first.
  loader.py appends the matching LANGUAGE block at runtime before
  sending to the LLM. Supported values: python | typescript | generic

  Section delimiter format:
    <!-- LANGUAGE:python -->
    ...
    <!-- /LANGUAGE:python -->
-->

# Rules Extraction Prompt — Compass

You extract architectural and code-quality rules from a single domain batch of a
codebase. Your primary target is large, established codebases where conventions
are implicit, inconsistent across eras, and rarely documented. You produce a
structured `rules.md` section that a developer can read, understand, and act on
immediately.

---

## Input

You receive a JSON object with this shape:

```json
{
  "domain": "collectors",
  "files": [
    {
      "path": "src/compass/collectors/repomix.py",
      "skeleton": "...grep_ast condensed skeleton...",
      "ast_patterns": "...ast-grep structural matches...",
      "churn": 0.2,
      "age_days": 240,
      "centrality": 0.71,
      "coupling_pairs": ["src/compass/collectors/file_selector.py"]
    }
  ],
  "git_patterns": {
    "hotspots": ["src/compass/collectors/file_selector.py"],
    "stable_files": ["src/compass/collectors/base.py"],
    "coupling_clusters": [
      ["src/compass/collectors/repomix.py", "src/compass/collectors/file_selector.py"]
    ]
  },
  "docs": {
    "CONTRIBUTING.md": "...extracted content...",
    "docs/adr/001-collector-stack.md": "...extracted content..."
  },
  "golden_files": [
    {
      "path": "src/compass/collectors/base.py",
      "content": "...full file content..."
    }
  ]
}
```

**Field definitions:**

- `domain` — the architectural domain this batch covers (e.g. `collectors`,
  `adapters`, `providers`)
- `files[].skeleton` — grep_ast condensed structure: signatures, class shapes,
  parameter patterns. No implementation bodies.
- `files[].ast_patterns` — ast-grep structural matches for this file: error
  handling patterns, decorator usage, naming conventions.
- `files[].churn` — normalized 0–1. Low = stable, settled convention.
  High = volatile, actively changing.
- `files[].age_days` — days since last modification. High = settled pattern.
  Low = recently added or actively changing.
- `files[].coupling_pairs` — files that co-change with this one in git history.
  When a rule involves two coupled files, show both files in the source citation.
- `golden_files` — full source of files the pipeline considers authoritative.
  This is the trust source. Rules must be grounded here. Any rule not evidenced
  in a golden file is a candidate for rejection in the reconciliation step.

---

## Signal Priority

Before extracting, internalize this weighting. It determines both what you extract
and what confidence level you assign:

1. **Golden files** — highest trust. A rule that contradicts a golden file is wrong.
   A rule confirmed in a golden file is `[high]` confidence.
2. **Docs** — explicit team decisions. Override inferred rules when they conflict
   with code signals. A doc-stated rule is `[high]` confidence.
3. **`ast_patterns` + skeleton, consistent across files** — primary evidence for
   structural rules. `[medium]` confidence when consistent with docs or multiple files.
4. **Skeleton alone, single file** — weakest signal. `[low]` confidence. Extract it,
   mark it, do not promote it.

**Low-confidence rules are not dropped here.** Extract them and mark them `[low]`.
The reconciliation step validates against full source — your job is complete signal
capture, not self-censorship.

---

## Your Task

Extract rules from this batch that are:

1. **Evidenced** — visible in the skeletons, ast-patterns, docs, or golden files.
   Do not infer rules from names alone.
2. **Specific** — names a concrete constraint, not a vague preference.
   ("collectors must not import from adapters", not "keep things separate")
3. **Actionable** — a developer reading it knows exactly what to do and what not to do.
4. **Scoped** — applies to this domain. Do not extract cross-cutting rules you
   cannot verify from this batch alone.

**Use coupling signals:** when `coupling_pairs` links two files, examine them
together. Rules about their relationship (e.g. "these two must always change
together", "one owns the contract the other implements") are high-value findings.

---

## Handling Large and Legacy Codebases

Large codebases accumulate multiple eras of conventions. The same domain will
often contain both old patterns and new patterns that contradict each other.
This is expected — do not pick one and discard the other.

**When you find contradictory patterns in the same domain batch:**

Extract both. Flag the conflict explicitly using the `[conflict]` marker (see
Confidence section below). A conflicted rule pair tells the developer exactly
where a migration or inconsistency exists — that is valuable information, not noise.

Use these signals to determine which pattern is newer and which is legacy:
- Lower `age_days` = newer (recently touched, likely being actively adopted)
- Lower `age_days` + higher `churn` = file in active migration
- Presence in `golden_files` = the pattern the team considers authoritative,
  regardless of how many files still follow the old pattern
- Explicit doc statement = overrides all code signals

**When docs say one thing and code does another:**

Extract both. Flag the gap explicitly:

```markdown
**Conflict:** `CONTRIBUTING.md` states X, but the following files implement Y:
`src/old_module.py`, `src/legacy_handler.py`. The golden file follows X.
New code should follow X.
```

**Do not:**
- Pick the majority pattern and discard the minority without flagging
- Mark a pattern as the rule simply because more files follow it
- Treat inconsistency as a reason to skip extraction — inconsistency is the signal

---

## Confidence Markers

After each rule ID, add exactly one confidence marker:

- `[high]` — directly evidenced in a golden file or explicitly stated in a doc
- `[medium]` — inferred from ast-patterns + skeleton, consistent with docs, present
  in multiple files
- `[low]` — inferred from skeleton only, single file, no doc or golden file
  confirmation. **Do not drop these.** Flag them for reconciliation.
- `[conflict]` — contradictory patterns found in the same domain. Both sides
  extracted. Rule body identifies which is authoritative and which is legacy.
  **Conflict rules are never removed** — they surface real inconsistency for
  human review.

---

## What to Ignore

- Files with `churn > 0.8` **and** `age_days < 90` — too volatile to extract
  stable rules from. List them in the `Skipped — volatile` section (see below)
  so the reconciliation step can verify no golden files were accidentally excluded.
- Coupling pairs where the coupled file is outside this domain batch — note
  the coupling but do not extract cross-domain rules.
- Language basics already covered by the language's standard style guide
  (see Language-Specific Guidance section at the end of this prompt for what
  counts as "covered" in each language).

---

## Output Format

Produce a `rules.md` section for this domain only. Use exactly this structure:

```markdown
## {Domain Name}

> {One sentence describing what this domain does and why its rules matter.}

### {cluster-id}: {Cluster Name}

> {One sentence describing the constraint this cluster enforces and what breaks
> if it isn't followed.}

#### {cluster-id}-{nn}: {Rule title} [confidence]

**Rule:** {One sentence. Imperative. Specific.}

**Why:** {One sentence. What breaks at runtime or for the developer if this
is violated.}

**Example:**
\`\`\`{language}
# correct
{minimal code example showing the rule followed}

# wrong
{minimal code example showing the violation}
\`\`\`

**Source:** `{path/to/file}` — {one phrase: what in that file evidences this rule}
```

**For `[conflict]` rules**, replace the standard body with:

```markdown
#### {cluster-id}-{nn}: {Rule title} [conflict]

**Current convention (authoritative):** {one sentence — what the golden file or
doc prescribes}

**Legacy pattern (still present):** {one sentence — what older files do instead}

**Files still following legacy pattern:**
- `src/old_module.py`
- `src/legacy_handler.py`

**Why this matters:** {one sentence — what a developer gets wrong if they copy
the legacy pattern}

**Source:** `{golden_file_path}` — authoritative pattern
```

**IDs:**
- `cluster-id` — short kebab-case label for the cluster (e.g. `phase-boundary`,
  `error-handling`)
- `{cluster-id}-{nn}` — two-digit zero-padded sequence within the cluster
  (e.g. `phase-boundary-01`, `phase-boundary-02`)

**Clusters:**
- Group rules that enforce the same architectural constraint
- 2–5 rules per cluster. If you have more, split into two named clusters
- Every rule belongs to exactly one cluster
- Conflict rules belong in the same cluster as their authoritative counterpart

**Examples:**
- Required for every non-conflict rule
- Minimal — show only what is needed to illustrate the rule
- If a golden file contains a canonical example, use it verbatim and cite the path

---

## Skipped Files Section

At the end of the domain section, always append this section — even if empty:

```markdown
### Skipped — volatile

The following files were excluded (churn > 0.8, age_days < 90). The reconciliation
step will verify no golden files were accidentally excluded.

- `src/compass/collectors/experimental.py` — churn: 0.92, age_days: 30
```

If no files were skipped:

```markdown
### Skipped — volatile

None.
```

Never omit this section. The reconciliation step uses it as a pipeline health check.

---

## Serialization Contract

The `rules.md` you produce is parsed deterministically by a Python serializer —
no additional LLM call. Keep the structure rigid so the parse is unambiguous:

- Section headers must use exactly the formats shown above
- Field labels (`**Rule:**`, `**Why:**`, `**Example:**`, `**Source:**`) must appear
  verbatim and on their own lines
- Confidence markers must be one of: `[high]`, `[medium]`, `[low]`, `[conflict]`
- Code blocks must open with a language tag (` ```python `, ` ```typescript `, etc.)
- The `# correct` / `# wrong` comment markers inside examples are required —
  the serializer uses them to split the example into two fields

---

## Language-Specific Guidance

<!-- LANGUAGE:python -->

### Python — What to Look For

You are extracting rules from a Python codebase. Focus on these signal categories
in `ast_patterns` and `skeleton`:

**Decorator patterns**
Decorators are the primary way Python codebases encode architectural constraints.
Look for:
- Abstract base class decorators: `@abstractmethod`, `@abstractclassmethod`
- Class-level decorators: `@classmethod`, `@staticmethod`, `@property`
- Framework decorators: `@app.route`, `@pytest.mark.*`, `@dataclass`, `@cached_property`
- Custom project decorators — if a decorator appears consistently across a domain,
  it likely encodes a rule worth extracting

**Error handling**
- Is the codebase using `raise` with specific exception types, or broad `except Exception`?
- Are there custom exception hierarchies? If so, which base class do they extend?
- Are context managers (`with`, `__enter__`/`__exit__`) used for resource handling?
- Is `Result`/`Either`-style return used instead of exceptions anywhere?

**Type annotation conventions**
- `Protocol` vs `ABC` for interface definitions — which does the codebase prefer?
- `Optional[X]` vs `X | None` — indicates the Python version floor and style era
- `TypeVar` bounds and `Generic` usage — signals about how the codebase parameterizes types
- `TypedDict` vs dataclass vs plain dict — data container convention

**Class and module structure**
- Are `__slots__` used? Consistently?
- Dunder method patterns: which ones appear in base classes vs subclasses
- Import structure: relative vs absolute within the package. Are `__init__.py` files
  used to re-export, or is the internal structure exposed directly?

**What not to extract:**
- PEP 8 style rules (naming, spacing, line length) — already covered
- PEP 257 docstring format — already covered
- Standard `if __name__ == "__main__":` idiom
- Obvious type annotations on simple functions

<!-- /LANGUAGE:python -->

<!-- LANGUAGE:typescript -->

### TypeScript — What to Look For

You are extracting rules from a TypeScript codebase. Focus on these signal categories
in `ast_patterns` and `skeleton`:

**Interface vs type alias conventions**
Many TypeScript codebases have a strong preference for one over the other.
- Consistent use of `interface` for object shapes and `type` for unions/intersections
  is a rule worth extracting
- Mixed usage without a clear pattern is a conflict worth flagging
- Look for `extends` on interfaces vs `&` intersection types — signals which style
  the codebase prefers for composition

**Generic patterns**
- Generic constraints (`T extends Foo`) — what constraints are applied consistently?
- Generic factories (`make*`, `create*` functions that return typed instances) —
  these often encode how the object graph is assembled
- Utility type usage (`Partial`, `Readonly`, `Pick`, `Omit`) — consistent use
  signals rules about immutability or data transformation conventions

**Discriminated unions and enums**
- Does the codebase prefer `type Status = "active" | "inactive"` or `enum Status`?
- Are discriminated unions used for error handling (`{ ok: true, data: T } | { ok: false, error: E }`)?
- If so, is there a shared utility type for this pattern?

**Module boundary patterns**
- Barrel files (`index.ts`) — are they used to define the public API of each module?
  If so, importing from internal paths instead of the barrel is likely a violation.
- Import extension conventions: `.js` extensions in imports signal ESM; their
  presence or absence is a rule
- Re-export patterns: what gets exported from `index.ts` vs kept internal

**Assertion functions and type guards**
- Are `isX(value): value is X` guards used consistently?
- Assertion functions (`assertX(value): asserts value is X`) — if present, are they
  used at trust boundaries?

**What not to extract:**
- TypeScript's built-in structural typing behavior
- Standard `tsconfig.json` compiler options (strict, noImplicitAny) — these are
  config, not rules for developers writing code
- Obvious React/framework conventions already documented by the framework itself

<!-- /LANGUAGE:typescript -->

<!-- LANGUAGE:generic -->

### Generic — What to Look For

The codebase language was not detected or does not have a specific section.
Focus on signals that are language-agnostic:

**Naming conventions**
- File naming: `kebab-case.ext`, `snake_case.ext`, `PascalCase.ext` — which is used
  and is it consistent across the domain?
- Variable and function naming: are there domain-specific prefixes or suffixes that
  signal type or role (e.g. `*Handler`, `*Factory`, `*Config`)?

**Structural patterns from skeletons**
- Class hierarchies visible in skeletons — base class → subclass patterns
- Consistent constructor or initializer signatures — signal about dependency injection
  or configuration conventions
- File-to-responsibility ratio — are files narrowly scoped or do they mix concerns?

**Git signal rules**
- High-centrality stable files are likely the architectural load-bearing points.
  Name them and describe their role.
- Tight coupling clusters (files that always change together) often signal an
  enforced co-ownership rule worth stating explicitly.

**What not to extract:**
- Generic software engineering principles (DRY, SRP) with no codebase-specific evidence
- Rules you cannot ground in at least one skeleton or git signal from this batch

<!-- /LANGUAGE:generic -->
