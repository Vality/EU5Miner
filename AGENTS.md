# Agent Guidelines

`packages/core/` is the single Python distribution `eu5miner`. It contains the core library and, under `src/eu5miner/{mcp,gui}/`, the optional MCP server and Kivy desktop UI submodules. Optional extras: `[mcp]`, `[gui]`, `[all]`.

## Conventions

- Python 3.12, src layout, hatchling.
- Ruff + mypy strict on the whole `eu5miner` package.
- Pytest collects everything under `packages/core/tests/`. Cross-package consumer tests live in `packages/core/tests/{mcp,gui}/test_cross_package_consumer.py`.
- Display names match module paths: `eu5miner-mcp` for `eu5miner.mcp`, `eu5miner-gui` for `eu5miner.gui`.

## Commands

```bash
# Sync everything
uv sync --extra=dev

# Test everything
cd packages/core && uv run pytest

# Lint everything
uv run ruff check .

# Type check
uv run mypy packages/core/src

# Build the wheel
(cd packages/core && uv build --out-dir $PWD/dist)
```

## Do not

- Recreate `packages/mcp/` or `packages/gui/` as separate distributions.
- Edit a sibling submodule from a PR targeted at a different submodule.
