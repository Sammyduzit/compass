# Brief: Foundation

Your job is to set up the **project scaffold** — the files that every other module imports or depends on. This includes the package config, shared utilities, error definitions, and the config dataclass. Nothing fancy, but it needs to be solid.

This is the first thing that needs to be done alongside the domain models. Other teams are waiting on you.

---

## What you're building

```
pyproject.toml
compass/__init__.py
compass/__main__.py
compass/errors.py
compass/config.py
compass/log.py
compass/paths.py
```

---

## Reference files — read these first

- **`FINAL.md`** → sections "Prerequisites", "CLI", "Configuration", "Distribution"
- **`STRUCTURE.md`** → sections `compass/config.py`, `compass/errors.py`, `compass/prerequisites.py`

---

## Part 1 — pyproject.toml

- What is the package name, entry point, and minimum Python version?
- Which dependencies need to be listed? (hint: check the Prerequisites section in FINAL.md)
- Which dependencies are dev-only? (pytest etc.)
- How do you define the `compass` CLI command as an entry point?
- How do you define a `[dev]` extras group so `pip install -e ".[dev]"` installs test dependencies?

---

## Part 2 — errors.py

The full exception hierarchy lives here. Everything Compass can raise is defined in this file.

- What is the base exception class?
- What subclasses does it have? (See STRUCTURE.md → `compass/errors.py` for the full tree)
- What information should each exception carry in its message?
- `PrerequisiteError` needs to include install instructions — how will you structure the message so it's useful to the user?
- `SchemaValidationError` needs to communicate what failed validation and why — what does that message look like?

---

## Part 3 — config.py

`CompassConfig` is a dataclass. It's created by `cli.py` and passed unchanged to `runner.run()`.

- What fields does it need? (See STRUCTURE.md → `compass/config.py` table)
- What are the types? Which fields are optional?
- What are the default values?
- Should it be frozen? Why or why not?

---

## Part 4 — log.py

A thin wrapper around Python's stdlib `logging`. One rule: the file must be named `log.py`, not `logging.py` (that would shadow the stdlib module and break everything).

- What's the simplest useful logger setup for a CLI tool?
- Should log level be configurable? If so, how?

---

## Part 5 — paths.py

Centralizes all `.compass/` path logic so nothing else hardcodes directory names.

- Where does Compass write its output? (See FINAL.md → "Output" section)
- What paths need to be computable given a `target_path`?
  - `.compass/` directory
  - `analysis_context.json`
  - `repo_state.json`
  - `output/rules.yaml`
  - `output/summary.md`

---

## Part 6 — __init__.py and __main__.py

- `__init__.py` — what should be exported from the top-level package, if anything?
- `__main__.py` — what does it need to do so that `python -m compass` works?

---

## Part 7 — Commit Convention Hook (pre-commit)

We enforce a consistent commit message format across all contributors. Set this up as your last step.

**Add `pre-commit` as a dev dependency in `pyproject.toml`.**

**Create `.pre-commit-config.yaml`** in the repo root. Define a `commit-msg` hook that enforces a commit message format — the format itself is your call. Document your decision clearly so everyone knows what's valid.

Once merged, **write a message to all other teams** telling them:
- What was set up (commit convention hook via pre-commit)
- What everyone needs to run once locally:
  ```bash
  pip install pre-commit
  pre-commit install --hook-type commit-msg
  ```
- The commit message format you decided on

---

## Part 8 — Test Infrastructure

Set up the test scaffolding that all other teams build on. No test logic here — just the infrastructure.

**Directory structure to create:**
```
tests/
├── conftest.py
├── unit/
│   └── __init__.py
├── integration/
│   └── __init__.py
└── fixtures/
    ├── setup.sh          ← idempotent script that initialises all 3 fixture repos
    ├── sample_repo_minimal/
    ├── sample_repo_python/
    └── sample_repo_typescript/
```

**`pyproject.toml`** — add pytest config and dev dependencies:
```toml
[tool.pytest.ini_options]
addopts = "--ignore=tests/integration"

[tool.pytest.ini_options.markers]
integration = "marks tests as integration (deselect with '-m not integration')"
```

Add a `conftest.py` option so `pytest --run-integration` includes integration tests. See TESTING.md → "Test Tiers" for the exact CLI behaviour expected.

**Fixture repos** — read TESTING.md → "Fixtures" for what each repo must contain. `setup.sh` must be idempotent: running it twice produces the same result. CI recreates fixtures from this script — do not commit `.git/` directories.

---

## Definition of done

- [ ] `pip install -e ".[dev]"` works without errors
- [ ] `compass --help` prints something (even if it does nothing yet)
- [ ] All exceptions in `errors.py` match the hierarchy in STRUCTURE.md
- [ ] `CompassConfig` fields match the table in STRUCTURE.md exactly
- [ ] No file named `logging.py` anywhere in the package
- [ ] `.pre-commit-config.yaml` committed and tested locally (invalid message blocked, valid message passes)
- [ ] `tests/` directory structure created with `conftest.py`, `unit/`, `integration/`, `fixtures/`
- [ ] `setup.sh` is idempotent and creates all 3 fixture repos with scripted git history
- [ ] `pytest` runs (0 tests collected is fine) without errors
- [ ] `pytest --run-integration` works as a separate pass
