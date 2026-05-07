# Compass

Compass helps you get oriented in an unfamiliar codebase.

It scans a repository and generates two useful outputs:

- `summary.md` and `summary.json`: a clear overview of what the codebase does and where to start reading
- `rules.yaml`: a structured set of project-specific engineering rules and conventions

The goal is simple: give a new engineer a faster way into a repository without asking them to read everything from scratch.

## What Compass Produces

After a run, Compass writes its artifacts into the target repository:

```text
target-repo/
└── .compass/
    ├── analysis_context.json
    ├── repo_state.json
    └── output/
        ├── rules.md
        ├── rules.yaml
        ├── summary.md
        └── summary.json
```

If you want to see real output before running the tool, check the examples in this repo:

- [examples/summary.md](examples/summary.md)
- [examples/rules.yaml](examples/rules.yaml)
- [examples/analysis_context.json](examples/analysis_context.json)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sammyduzit/compass
cd compass
```

### 2. Install Compass

Compass currently runs as a local CLI tool:

```bash
pip install -e .
```

For development work, install the dev extras instead:

```bash
pip install -e ".[dev]"
```

### 3. Make sure the required tools are available

Compass checks its prerequisites at runtime and shows install instructions if something is missing.

You will need:

- Python 3.11+
- `git`
- `ast-grep`
- `repomix`
- either the `claude` CLI or the `codex` CLI

`codebase-memory-mcp` is downloaded automatically on first run when supported on your platform.

Common install commands:

```bash
brew install ast-grep
brew install repomix
```

Or:

```bash
cargo install ast-grep
npm install -g repomix
```

## Basic Usage

Run Compass against a repository by passing the target path and selecting one or more adapters.

Generate rules only:

```bash
compass /path/to/repo --adapters rules
```

Generate a summary only:

```bash
compass /path/to/repo --adapters summary
```

Generate both outputs:

```bash
compass /path/to/repo --adapters rules,summary
```

Run all available adapters:

```bash
compass /path/to/repo --adapters all
```

Choose a provider explicitly:

```bash
compass /path/to/repo --adapters summary --provider claude
compass /path/to/repo --adapters summary --provider codex
```

Force a fresh analysis instead of reusing saved context:

```bash
compass /path/to/repo --adapters rules --reanalyze
```

## Configuration

You can set defaults in a config file:

- project-level: `.compass/config.yaml`
- global: `~/.compass/config.yaml`

Example:

```yaml
default_provider: claude
lang: auto
```

## How It Works

Compass works in two steps:

1. It collects information from the repository, such as structure, history, and patterns.
2. It turns that information into readable outputs for onboarding and project conventions.

That collected context is saved so you can re-run outputs without repeating the full analysis every time.

## Current Scope

Compass is built for:

- onboarding into an unfamiliar repository
- capturing project-specific engineering rules
- generating a quick, structured overview for humans and downstream tools

It is not meant to:

- modify code
- replace documentation entirely
- act as a linter or formatter

## More Context

For architecture and implementation decisions, see:

- [FINAL.md](FINAL.md)
- [FRONTEND.md](FRONTEND.md)
