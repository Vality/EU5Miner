# Contributing

Thanks for contributing to EU5Miner.

## Scope

This repository is the umbrella for the single Python distribution `eu5miner`, with the MCP server and Kivy desktop UI shipped as optional submodules under `eu5miner.mcp` and `eu5miner.gui`.

- Keep parser, VFS, and domain-model logic in the core library rather than the optional submodules.
- Preserve the project layering: install discovery, VFS, generic format readers, semantic helpers, then domain adapters.
- Prefer small, typed, test-backed changes.
- Keep the default workflow buildable without a local EU5 install unless real-file validation is the point of the change.

## Setup

Clone the umbrella and sync once:

```bash
git clone https://github.com/Vality/EU5Miner.git
cd EU5Miner
uv sync --extra=dev
```

A Windows setup script is provided at `scripts/setup-centralized-uv.ps1` for users who prefer a centralized venv under `%USERPROFILE%/.venvs/EU5Miner`.

## Validation

Run these before opening a pull request:

```bash
# Sync everything
uv sync --extra=dev

# Test the package
cd packages/core && uv run pytest

# Lint everything
uv run ruff check .

# Type check the package
uv run mypy packages/core/src

# Build the wheel
(cd packages/core && uv build)
```

Use `uv run python -m pytest -m broad` only when you intentionally need the broader optional install-backed sweep.

## Pull Requests

- Describe the user-visible change and the layer or submodule it belongs in.
- Mention any public API, packaging, or contract changes.
- Include the validation commands you ran.
- One submodule per PR when feasible — open separate PRs for changes that span core plus an optional submodule.
