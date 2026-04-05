# Contributing

Thanks for contributing to EU5Miner.

## Scope

This repository is the core typed library.

- Keep parser, VFS, and domain-model logic here rather than in downstream GUI or MCP repos.
- Preserve the project layering: install discovery, VFS, generic format readers, semantic helpers, then domain adapters.
- Prefer small, typed, test-backed changes.
- Keep the default workflow buildable without a local EU5 install unless real-file validation is the point of the change.

## Setup

Recommended setup:

```powershell
.\scripts\setup-centralized-uv.ps1
```

One-off setup:

```powershell
uv sync --extra dev
```

## Validation

Run these before opening a pull request:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

Use `uv run python -m pytest -m broad` only when you intentionally need the broader optional install-backed sweep.

## Pull Requests

- Describe the user-visible change and the layer it belongs in.
- Mention any public API, packaging, or contract changes.
- Include the validation commands you ran.