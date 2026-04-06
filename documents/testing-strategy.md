# Testing Strategy

## Core Principle

Tests are part of the product design. The library should be built against real EU5 files from the installed game so parser and discovery logic reflect the game as shipped.

## Test Categories

### Real-install tests

These tests should run against the local EU5 install when present.

They validate:

- install discovery
- expected phase roots
- representative file presence
- basic structural parsing of real files

### Unit tests

These tests validate smaller helper behavior using short inline examples.

They validate:

- path resolution
- script construct detection
- localization parsing
- CSV parsing
- metadata parsing

### CLI workflow tests

These tests should primarily call `eu5miner.cli.main(...)` directly with synthetic temp-path installs and mods.

They validate:

- command exit codes
- stdout report shape
- stderr diagnostics for `note:` advisories, `warning:` conflicts, and `error:` failures
- non-destructive dry-run planning
- filesystem side effects for apply commands
- overwrite refusal paths and malformed argument/mapping errors

The CLI test suite should prefer synthetic installs for mod-writing workflows so tests can freely create and overwrite files without touching a real EU5 install.

Real-install CLI coverage should stay narrow and read-only, focused on smoke-testing commands like install inspection, merged file listing, and representative-file analysis.

For mutating CLI commands, prefer a layered strategy:

- parser/helper unit tests for argument normalization and mapping expansion
- command-level tests via `main(...)` and `capsys`
- temp-path end-to-end tests that assert the actual written files and metadata
- only add subprocess-level console-script tests later if packaging behavior itself becomes important

### Reusable integration surfaces

The test suite should maintain one or more reusable synthetic integration surfaces that model a small but realistic install and mod stack.

These surfaces should be stable fixtures rather than ad hoc per-test setup when validating higher-level workflows.

They validate:

- coordination between VFS precedence, mod planning, materialization, and CLI wrappers
- replace_path advisories versus shadowing warnings on a consistent source stack
- repeated high-level workflows against the same known install/mod relationships as the tool surface grows

The goal is not to freeze large committed fixture mods unless they become clearly valuable. A synthetic but reusable fixture layer is sufficient as long as it stays consistent and readable.

### Future golden tests

As the CST and writer arrive, the suite should add:

- parse-tree golden tests
- round-trip serialization tests
- local-format-preservation tests
- overlay precedence tests

## Timeout Policy

- The default `uv run pytest` baseline should stay warning-free even when plugin-specific pytest ini options are not active.
- When `pytest-timeout` is available in the synced development environment, the suite applies a global 30 second per-test timeout during `pytest_configure`.
- Parser-sensitive real-file tests can override that default with tighter but realistic per-test timeouts.
- Timeouts should be high enough to avoid flaky failures on slower machines, but low enough to surface accidental algorithmic blowups during development.

## Real-File Policy

- Prefer tests that validate the parser against representative shipped files.
- Keep the test corpus centered on the major moddable text file families.
- Skip real-install tests cleanly if the install is unavailable.

## Required Baseline Validation

Use this install-independent baseline for the normal contributor and cloud-agent loop:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

## Optional Broad Sweep

- Keep one marker-backed broad sweep for wider real-install coverage and cross-helper integration.
- Run it explicitly with `uv run python -m pytest -m broad` when auditing coverage across the current representative matrix.
- Keep the `broad` suite out of the default fast loop so focused parser iteration stays cheap.
