# Contributing

Thanks for contributing to EU5MinerGUI.

## Scope

This repo is the thin application layer on top of the core `eu5miner` library.

- Keep parser, VFS, and domain-model logic in the core library.
- Prefer small, typed, test-backed changes.
- Keep the default workflow install-free when practical.

## Setup

Use the centralized `uv` environment described in `documents/development-environment.md` or run:

```powershell
.\scripts\setup-centralized-uv.ps1
uv sync --extra dev
```

## Validation

Run the standard checks before opening a pull request:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

## Pull Requests

- Describe the user-visible change and why it belongs in this repo.
- Add or update tests when behavior changes.
- Keep documentation updates close to the code change when needed.
- Use the pull request template checklist.