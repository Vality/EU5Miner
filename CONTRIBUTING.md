# Contributing

Thanks for contributing to EU5Miner.

## Scope

This repository is the umbrella for three coordinated Python packages:

- `packages/core/` — `eu5miner` core library and CLI
- `packages/mcp/` — `eu5miner-mcp` MCP server
- `packages/gui/` — `eu5miner-gui` Kivy desktop UI

- Keep parser, VFS, and domain-model logic in `packages/core/` rather than downstream packages.
- Preserve the project layering: install discovery, VFS, generic format readers, semantic helpers, then domain adapters.
- Prefer small, typed, test-backed changes.
- Keep the default workflow buildable without a local EU5 install unless real-file validation is the point of the change.

## Setup

Clone the umbrella and sync the whole workspace:

```bash
git clone https://github.com/Vality/EU5Miner.git
cd EU5Miner
uv sync --all-packages --extra=dev
```

A Windows setup script is provided at `scripts/setup-centralized-uv.ps1` for users who prefer a centralized venv under `%USERPROFILE%/.venvs/EU5Miner`.

## Validation

Run these before opening a pull request:

```bash
# Sync everything
uv sync --all-packages --extra=dev

# Test the package you changed
cd packages/<name> && uv run pytest

# Lint everything
uv run ruff check .

# Type check the package you changed
uv run mypy packages/<name>/src

# Build all three wheels
uv build --all-packages
```

Use `uv run python -m pytest -m broad` only when you intentionally need the broader optional install-backed sweep.

## Pull Requests

- Describe the user-visible change and the layer or package it belongs in.
- Mention any public API, packaging, or contract changes.
- Include the validation commands you ran.
- One package per PR when feasible — open separate PRs for changes that span two sub-packages.
- Version bumps across the three packages must move in lockstep.
