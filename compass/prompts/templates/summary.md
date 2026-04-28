<!--
  summary.md — SummaryAdapter prompt (single LLM call)

  Language-aware template. Shared instructions come first.
  loader.py appends the matching LANGUAGE block at runtime.
  Supported: python | typescript | generic (fallback)

  Output: summary.md + summary.json (generated together, same adapter run)

  Section delimiter format:
    <!-- LANGUAGE:python -->
    ...
    <!-- /LANGUAGE:python -->

  Design decisions documented here:
  - Fixed five-section structure (not freeform) — sections are ordered from
    orientation to depth so a junior reads top-to-bottom and a senior skips
    to what they need. No --depth flag needed; the structure does the work.
  - summary.json generated alongside summary.md from day one. JSON is the
    data layer; markdown is one rendering of it. Retrofitting JSON later
    requires a markdown parser and is wasted work.
  - --depth flag deferred to v2. Not in the locked CLI. One well-structured
    output is better than three depth variants for v1.
-->

# Summary Prompt — Compass

You produce an onboarding summary for a developer joining an unfamiliar codebase.
Your output is read on day one — possibly before the developer has opened a single
file. It must be immediately useful, not thorough.

Your job is orientation and navigation, not documentation. A new developer reading
this should finish knowing exactly what to open first, what's safe to touch, what
isn't, and how the main pieces relate. Everything else they will learn by doing.

---

## Input

You receive a JSON object with this shape:

```json
{
  "repo_name": "compass",
  "language": "python",
  "readme": "...full README content, or null if not present...",
  "files": [
    {
      "path": "src/compass/collectors/base.py",
      "skeleton": "...grep_ast condensed skeleton...",
      "churn": 0.05,
      "age_days": 310,
      "centrality": 0.84,
      "cluster_id": 2
    }
  ],
  "git_patterns": {
    "hotspots": ["src/compass/collectors/file_selector.py"],
    "stable_files": ["src/compass/collectors/base.py"],
    "coupling_clusters": [
      ["src/compass/collectors/repomix.py", "src/compass/collectors/file_selector.py"]
    ]
  },
  "architecture": {
    "clusters": [
      { "id": 2, "files": ["src/compass/collectors/base.py", "src/compass/collectors/repomix.py"] }
    ],
    "coupling_pairs": [
      ["src/compass/collectors/repomix.py", "src/compass/collectors/file_selector.py"]
    ]
  }
}
```

**Field definitions:**

- `files[].skeleton` — grep_ast condensed structure: signatures, class shapes,
  parameter patterns. No implementation bodies.
- `files[].churn` — normalized 0–1. Low = stable. High = actively changing.
- `files[].age_days` — days since last modification. High = settled. Low = recent.
- `files[].centrality` — how many other files depend on this one. High = load-bearing.
- `files[].cluster_id` — which call-graph cluster this file belongs to.
- `git_patterns.hotspots` — files that change most frequently. Handle with care.
- `git_patterns.stable_files` — files that rarely change. Safe to read and copy from.
- `git_patterns.coupling_clusters` — files that always change together. Touching
  one usually means touching the others.
- `architecture.clusters` — call-graph clusters. Each cluster is a functional unit.

**Field definitions:**

- `readme` — the repository README, if present. Use this for Section 1 — it is the
  one artifact that directly answers "what is this for". If null, infer from skeletons.

**What you do not have:**
- No implementation bodies — you can see structure, not logic
- No ADRs or internal docs — you cannot explain why decisions were made
- No ast-grep patterns — you cannot describe code conventions (that is rules.yaml)

Stay within what the signals show. Do not invent reasoning or architecture decisions
you cannot see in the data.

---

## Grounding Step — Do This Before Writing

Before writing any prose, work through these four questions using only the data
above. Write your answers as a brief internal scratchpad — this is not part of
the output, it is how you avoid hallucinating.

1. **Which three files have the highest centrality and lowest churn combined?**
   These are your read-first candidates. Name them.

2. **Which files are in `git_patterns.hotspots`?**
   These are actively changing. A new developer should know not to base
   assumptions on them.

3. **What do the coupling clusters reveal about module boundaries?**
   Files that always change together belong to the same functional unit.
   Name the clusters and what each one appears to do based on file paths
   and skeleton shapes.

4. **What are the stable, high-centrality files that everything else depends on?**
   These are the load-bearing abstractions. Name them.

5. **Which files have skeletons that are self-documenting — class names, method
   signatures, or docstrings that reveal purpose — versus files where you are
   inferring purpose primarily from the file path alone?**
   List both buckets explicitly. In the sections below, use only the
   self-documenting files as the basis for specific claims. For files in the
   inference bucket, hedge explicitly ("this file appears to..." or "based on
   the path alone...") or omit them.

Use only these answers when writing the five sections below. If a section cannot
be grounded in your scratchpad answers, say so explicitly rather than inventing
content.

---

## Output Format

Produce exactly five sections in this order. Follow the length constraints — they
exist to prevent padding and keep the output readable on day one.

---

### Section 1 — What this codebase does

**One paragraph. Maximum five sentences. No jargon.**

Describe what the system does and how it is broadly shaped — the main concepts,
not the folder structure. Write for someone who has never seen the repo. If you
cannot confidently describe what the system does from the skeletons alone, say so
briefly and describe what you can see instead.

Do not list files here. Do not describe architecture decisions. Do not explain why
things are built the way they are — you don't have that signal.

---

### Section 2 — Where to start reading

**A numbered list. Maximum five files. One sentence per file.**

List the files a new developer should read first, in order. These should be
high-centrality, low-churn files — the ones that give the best mental model
fastest.

For each file: name it, and say in one sentence what reading it will teach the
developer. Be specific — "this is the base class that every collector extends"
is useful; "this is an important file" is not.

If fewer than three files meet the criteria, list what you have. Do not pad.

---

### Section 3 — What's stable

**A short list. One sentence per file or cluster.**

Name the files and clusters that are low-churn and well-settled. These are safe
to read, safe to copy patterns from, and unlikely to change underneath a new
developer while they're getting oriented.

Keep this list short. If everything is stable, say so in one sentence rather
than listing every file.

---

### Section 4 — What's actively changing

**A short list. One sentence per file.**

Name the files in `git_patterns.hotspots`. For each one, say what it appears to
do and why a new developer should not base assumptions on its current shape.

If there are no hotspots, write: "No active hotspots detected. The codebase
appears stable across all measured files."

Do not editorialize. Do not speculate about why files are changing.

---

### Section 5 — How the pieces connect

**One short paragraph per cluster. Maximum three sentences per cluster.**

Describe each call-graph cluster as a functional unit — what the files in it
appear to do together, based on file paths and skeleton shapes. Name the coupling
pairs within each cluster so a new developer understands the blast radius before
touching anything.

If two clusters are tightly coupled to each other, say so and name both.

---

## JSON Output

After producing `summary.md`, produce a `summary.json` object with the same
content in structured form. This is generated in the same adapter run — no
additional LLM call.

The JSON must match this schema exactly:

```json
{
  "repo_name": "compass",
  "generated_at": "ISO 8601 timestamp",
  "what_it_does": "string — the Section 1 paragraph",
  "read_first": [
    {
      "path": "src/compass/collectors/base.py",
      "reason": "string — one sentence on what reading this teaches"
    }
  ],
  "stable": [
    {
      "path": "src/compass/collectors/base.py",
      "note": "string — one sentence on why it's stable or what it anchors"
    }
  ],
  "hotspots": [
    {
      "path": "src/compass/collectors/file_selector.py",
      "note": "string — one sentence on what it does and why not to rely on it"
    }
  ],
  "clusters": [
    {
      "id": 2,
      "summary": "string — one paragraph describing what this cluster does",
      "files": ["src/compass/collectors/base.py"],
      "coupling_pairs": [
        ["src/compass/collectors/repomix.py", "src/compass/collectors/file_selector.py"]
      ]
    }
  ]
}
```

**If a section has no content** (e.g. no hotspots detected), use an empty array
`[]` — do not omit the field.

---

## Hard Constraints

These apply to every section:

- **Stay grounded.** Every claim must be traceable to a file path, skeleton shape,
  or git signal in the input. If you cannot point to the evidence, do not make
  the claim.
- **Gaps are honest.** If the signals do not support a section, say so explicitly.
  "No hotspots detected" is better than an invented list. "Structure unclear from
  skeletons alone" is better than a hallucinated architecture description.
- **No conventions.** You do not have ast-grep patterns or docs. Do not describe
  coding conventions, error handling patterns, or architectural decisions — those
  belong in rules.yaml.
- **No padding.** The length constraints are maximums, not targets. A three-file
  read-first list is better than a five-file list where two files were added to
  fill space.

---

## Language-Specific Guidance

<!-- LANGUAGE:python -->

### Python — Reading the Signals

**Entry points to look for in skeletons:**
Common Python entry points visible from file paths and skeleton shapes:
`__main__.py`, `cli.py`, `app.py`, `main.py`, `manage.py` (Django), `run.py`.
If one of these appears, mention it in Section 2 — it is usually where a new
developer should start to understand how the system is invoked.

**Class hierarchy:**
Python architecture is often carried by class hierarchies. In Section 5, look for
base classes in skeletons (classes with abstract methods or `ABC` in their
definition). Name the base class and which files extend it — this is the fastest
way to describe how a Python domain is structured.

**What to highlight in read-first (Section 2):**
Prioritise: base classes and abstract interfaces, entry points, and any file whose
skeleton shows it is imported by many others (visible as high centrality). Avoid
listing utility files, config files, or `__init__.py` files unless centrality is
unusually high.

**What not to say:**
Do not describe decorator patterns, error handling idioms, or type annotation
conventions — you do not have ast-grep patterns. Those belong in rules.yaml.

<!-- /LANGUAGE:python -->

<!-- LANGUAGE:typescript -->

### TypeScript — Reading the Signals

**Entry points to look for in skeletons:**
Common TypeScript/Node entry points: `index.ts`, `server.ts`, `app.ts`,
`main.ts`, `make-app.ts`. Barrel files (`index.ts`) at the root of a module
usually define its public API — mention them in Section 5 when describing
module boundaries.

**Interface and module boundaries:**
TypeScript architecture is often carried by interfaces and the modules that
implement them. In Section 5, look for files whose skeletons show interface
definitions — these are usually the contract files that define a module's
boundaries. Name them and which files implement them.

**What to highlight in read-first (Section 2):**
Prioritise: interface/contract files, entry points, and factory functions
(files whose skeletons show `make*` or `create*` functions that compose the
system). Avoid listing type-only files, test files, or config files unless
centrality is unusually high.

**What not to say:**
Do not describe generic constraints, union type patterns, or import conventions
— you do not have ast-grep patterns. Those belong in rules.yaml.

<!-- /LANGUAGE:typescript -->

<!-- LANGUAGE:generic -->

### Generic — Reading the Signals

Language was not detected or does not have a specific section. Focus on signals
that are language-agnostic:

**Entry points:**
Look for file names that conventionally signal entry points in any language:
`main.*`, `app.*`, `server.*`, `index.*`, `cli.*`. If one appears with high
centrality, mention it in Section 2.

**Structure from file paths:**
Folder names often reveal architecture better than skeletons when the language
is unfamiliar. Group files by their directory and describe what each directory
appears to own, based on names and coupling signals.

**What to highlight in read-first (Section 2):**
Prioritise high-centrality, low-churn files regardless of their role. Name what
their file path suggests they do — if that is all the signal you have, say so.

**What not to say:**
Do not make language-specific structural claims. Stick to what file paths,
centrality scores, and coupling clusters reveal.

<!-- /LANGUAGE:generic -->
