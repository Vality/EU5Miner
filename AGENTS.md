# Agent Guidelines

This is a single uv workspace with three coordinated Python packages:
- `packages/core/` — `eu5miner` core library
- `packages/mcp/` — `eu5miner-mcp` MCP server
- `packages/gui/` — `eu5miner-gui` Kivy desktop UI

## Conventions

- Python 3.12, src layout, hatchling.
- Ruff + mypy strict on all three packages.
- Pytest per-package; cross-package consumer tests live alongside each downstream package.
- Version bumps are coordinated across all three packages (lockstep).
- Workspace root has the lockfile (`uv.lock`) and the `[tool.uv.workspace]` block; per-member `pyproject.toml` files hold the `[project]` metadata.

## Commands

```bash
# Sync everything
uv sync --all-packages --extra=dev

# Test one package
cd packages/<name> && uv run pytest

# Lint everything
uv run ruff check .

# Type check one package
uv run mypy packages/<name>/src

# Build all wheels
uv build --all-packages
```

## Do not

- Add per-member `uv.lock` files. The single root lockfile is the source of truth.
- Edit a sibling package's source from another package's PR — open separate PRs.
- Bump versions independently across the three packages. Lockstep only.
