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
