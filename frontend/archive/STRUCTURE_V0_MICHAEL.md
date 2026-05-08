# Structure

## Purpose

This document defines the intended project structure for the Python-based `Compass` CLI.
It describes:

- how the source code should be organized
- where generated artifacts belong
- which responsibilities belong to which package

The goal is to keep the codebase easy to navigate, easy to extend, and consistent with the two-phase architecture already defined for Compass:

```text
Collectors (no LLM) -> AnalysisContext -> Adapters (one LLM call each)
```

## Core Principles

- The implementation language is Python.
- Runtime artifacts do not belong inside the Compass source tree.
- The codebase should separate orchestration, domain models, collection, synthesis, and persistence.
- Prompt templates and output schemas should be first-class project assets.
- The target repository being analyzed owns the generated `.compass/` directory.
- Module names should describe one concrete responsibility. Avoid generic catch-all names like `models.py`, `helpers.py`, or `registry.py`.
- Domain data structures should use one file per model so ownership is obvious and navigation stays predictable.
- Package-local modules must not shadow Python standard library modules. For example, use `log.py`, not `logging.py`.

## Repository Layout Example

```text
compass/
├── README.md
├── pyproject.toml
├── .gitignore
├── examples/
│   ├── analysis_context.json
│   ├── rules.yaml
│   └── summary.md
├── tests/
│   ├── unit/
│   │   ├── test_cli.py
│   │   ├── test_context_store.py
│   │   ├── test_language_detection.py
│   │   ├── test_prerequisites.py
│   │   ├── test_repo_state_store.py
│   │   ├── test_rules_adapter.py
│   │   └── test_summary_adapter.py
│   ├── integration/
│   │   ├── test_run_rules.py
│   │   ├── test_run_summary.py
│   │   └── test_reanalyze_flow.py
│   └── fixtures/
│       ├── sample_repo_minimal/
│       ├── sample_repo_python/
│       └── sample_repo_typescript/
├── docs/
│   └── STRUCTURE.md
└── src/
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── config.py
        ├── paths.py
        ├── log.py
        ├── errors.py
        ├── language_detection.py
        ├── prerequisites.py
        ├── domain/
        │   ├── __init__.py
        │   ├── analysis_context.py
        │   ├── adapter_output.py
        │   ├── architecture_snapshot.py
        │   ├── git_patterns_snapshot.py
        │   ├── pipeline_contracts.py
        │   └── source_snapshot.py
        ├── collectors/
        │   ├── __init__.py
        │   ├── base.py
        │   ├── architecture.py
        │   ├── git_patterns.py
        │   ├── source_snapshot.py
        │   └── orchestrator.py
        ├── adapters/
        │   ├── __init__.py
        │   ├── base.py
        │   ├── rules.py
        │   ├── summary.py
        │   └── orchestrator.py
        ├── providers/
        │   ├── __init__.py
        │   ├── base.py
        │   └── claude.py
        ├── prompts/
        │   ├── __init__.py
        │   ├── loader.py
        │   └── templates/
        │       ├── rules.md
        │       ├── summary.md
        │       ├── rules_python.md
        │       └── rules_typescript.md
        ├── schemas/
        │   ├── __init__.py
        │   ├── rules_schema.py
        │   └── summary_schema.py
        ├── storage/
        │   ├── __init__.py
        │   ├── analysis_context_store.py
        │   ├── output_writer.py
        │   ├── repo_state_hash.py
        │   └── repo_state_store.py
        └── utils/
            ├── __init__.py
            ├── filesystem.py
            ├── json_io.py
            └── subprocess.py
```

## Package Responsibilities

### `src/compass/domain/`

Contains the core data structures and contracts of the application.

Examples:

- `AnalysisContext`
- adapter output models
- architecture, git pattern, and source snapshot models
- shared interfaces between collectors, adapters, and providers

Every domain structure should live in a dedicated module named after that structure. Do not add `models.py` or other generic containers for unrelated data classes.

This package should remain independent from CLI concerns and provider-specific subprocess logic.

### `src/compass/collectors/`

Contains Phase 1 of the pipeline.

Collectors gather repository information without calling an LLM. They should produce normalized data that can be persisted into `AnalysisContext`.

Typical responsibilities:

- architecture extraction
- git pattern extraction
- compressed source collection
- collector orchestration

### `src/compass/adapters/`

Contains Phase 2 of the pipeline.

Adapters consume selected sections of `AnalysisContext`, build prompts, call a provider, validate the structured response, and write output artifacts.

Each adapter should:

- declare which context sections it needs
- declare which schema validates its output
- produce exactly one output artifact

### `src/compass/providers/`

Encapsulates LLM provider integrations.

In v1, this should primarily contain the `claude` CLI integration. The provider package should hide subprocess details from the rest of the system and expose a small, stable interface for synthesis.

Do not add a provider registry until a second real provider exists. A small conditional in `providers/base.py` is the preferred v1 design.

### `src/compass/prompts/`

Contains prompt loading and template files.

Prompt templates should be versioned with the codebase and treated as implementation assets, not inline strings scattered across Python modules.

The `templates/` folder is the right place for:

- generic prompts
- language-specific prompt variants
- future adapter prompt variants

### `src/compass/schemas/`

Contains output schemas used to validate structured LLM responses.

Each adapter should have an explicit schema so invalid provider output fails early and predictably.

### `src/compass/storage/`

Contains persistence logic for runtime artifacts.

This package is responsible for:

- writing and reading `analysis_context.json`
- writing generated output files
- storing repository state metadata used for staleness detection
- computing repository-state hashes used by staleness detection

Hashing for staleness checks belongs here because it exists to support repository-state persistence. If broader hashing needs appear later, that can be revisited then.

This keeps filesystem persistence isolated from collectors and adapters.

### `src/compass/language_detection.py`

Contains repository language detection used for `--lang auto`.

This module should infer the dominant language or project type from the target repository and feed prompt-template selection. Keep the logic explicit and lightweight rather than scattering language checks across adapters or prompt loaders.

### `src/compass/prerequisites.py`

Contains startup checks for required external tooling and environment preparation.

This module should own checks such as:

- required CLIs being installed
- MCP/index availability
- repomix availability
- provider CLI availability

`cli.py` should call into this module on startup instead of embedding prerequisite logic inline.

### `src/compass/utils/`

Contains low-level shared helpers that do not belong to a domain package.

Examples:

- JSON file helpers
- subprocess wrappers
- filesystem utilities

Keep this package small. If logic becomes domain-specific, move it into the relevant package instead.

## Runtime Output Location

Generated artifacts should not be written into the Compass repository itself.

They belong inside the target repository being analyzed:

```text
target-repo/
└── .compass/
    ├── analysis_context.json
    ├── repo_state.json
    └── output/
        ├── rules.yaml
        └── summary.md
```

## Why `output/` Belongs Inside `.compass/`

- It keeps all Compass-owned generated files in one place.
- It avoids polluting the target repository root.
- It keeps persisted context and generated artifacts adjacent to each other.
- It makes cleanup, `.gitignore` rules, and reruns straightforward.

This means:

- `analysis_context.json` is the persisted Phase 1 artifact
- `output/` contains Phase 2 adapter artifacts
- `repo_state.json` stores the repository fingerprint used for staleness checks

## Recommended Growth Path

As the project evolves, new features should usually fit into one of these existing areas:

- new repository analysis logic goes into `collectors/`
- new generated artifact types go into `adapters/`
- new model providers go into `providers/`
- new language detection heuristics go into `language_detection.py`
- new prompt variants go into `prompts/templates/`
- new prerequisite checks go into `prerequisites.py`
- new persistence concerns go into `storage/`

This avoids a flat package full of unrelated modules and keeps the two-phase architecture visible in the filesystem.

## What Should Not Be Added Prematurely

Avoid adding extra top-level packages for speculative abstractions.

In particular, do not introduce separate folders for:

- services
- managers
- helpers
- engine
- core
- registries for single-implementation cases

unless a concrete implementation need appears that cannot be expressed clearly within the existing structure.

The structure should remain explicit and boring rather than abstract and ambiguous.

The same rule applies at the module level: prefer specific names and single-purpose files over generic containers.
