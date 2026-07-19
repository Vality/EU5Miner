# Migration: 0.7.x → 0.8.0 — Single-wheel consolidation

The MCP and GUI sub-projects have been merged into this repository's single `eu5miner` wheel. The PyPI distribution `eu5miner` is the only artifact published for the project.

## What changed

| Before | After |
|---|---|
| `pip install eu5miner-mcp` (PyPI) | `pip install eu5miner[mcp]` |
| `pip install eu5miner-gui` (PyPI) | `pip install eu5miner[gui]` |
| `pip install eu5miner[all]` pulling two extras | `pip install eu5miner[all]` (same surface) |
| `from eu5miner_mcp.X import Y` | `from eu5miner.mcp.X import Y` |
| `from eu5miner_gui.X import Y` | `from eu5miner.gui.X import Y` |
| Three `pyproject.toml` files | One (under `packages/core/`) |
| `[tool.uv.workspace]` with three members | None (single project) |
| `packages/{mcp,gui}/pyproject.toml` | Deleted |
| `eu5miner_mcp.__main__` (force-included) | `eu5miner.mcp.__main__` (default layout) |
| Display name `EU5MinerMCP` | Display name `eu5miner-mcp` |
| Display name `EU5MinerGUI` | Display name `eu5miner-gui` |

## Python imports

`from eu5miner import ...` continues to work unchanged for core symbols. MCP-specific symbols (`build_server`, `run_server`, `run_stdio_server`, `serve_stdio`) require `eu5miner[mcp]`. GUI-specific symbols (`DesktopController`, `BrowserModel`, etc.) require `eu5miner[gui]`.

## CLI entry points

All four scripts (`eu5miner`, `eu5miner-mcp`, `eu5miner-gui`, `eu5miner-gui-shell`) resolve from the unified wheel — install commands unchanged at the script level.

---

# Migration: pre-0.7.0 → 0.7.0

The MCP and GUI sub-projects have been merged into this repository as a uv workspace. The PyPI distribution names are unchanged.

## What changed

| Before | After |
|---|---|
| `git clone https://github.com/Vality/EU5MinerMCP.git` | `git clone https://github.com/Vality/EU5Miner.git && cd packages/mcp` |
| `git clone https://github.com/Vality/EU5MinerGUI.git` | `git clone https://github.com/Vality/EU5Miner.git && cd packages/gui` |
| `pip install eu5miner-mcp` (from PyPI) | `pip install eu5miner-mcp` (still works) **or** `pip install eu5miner[mcp]` |
| `pip install eu5miner-gui` (from PyPI) | `pip install eu5miner-gui` (still works) **or** `pip install eu5miner[gui]` |
| Standalone `pyproject.toml` per repo | `packages/<name>/pyproject.toml` under the umbrella |
| Per-repo `uv.lock` | Single root `uv.lock` |

## Python imports

**No changes.** `from eu5miner import ...`, `import eu5miner.inspection as inspection`, and all downstream imports continue to resolve by name.

## CLI entry points

**No changes.** `eu5miner`, `eu5miner-mcp`, `eu5miner-gui`, `eu5miner-gui-shell` all work the same as before.

## Archived repos

`Vality/EU5MinerMCP` and `Vality/EU5MinerGUI` are archived (read-only). All release tags up to and including v0.6.x remain accessible. No new development happens there.
