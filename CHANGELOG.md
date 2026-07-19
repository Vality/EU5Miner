# Changelog

## 0.8.0 — Single-wheel consolidation

### Breaking changes

- `eu5miner-mcp` and `eu5miner-gui` are no longer published as separate PyPI wheels. Install the MCP surface with `pip install eu5miner[mcp]`, the GUI surface with `pip install eu5miner[gui]`, or both with `pip install eu5miner[all]`.
- The MCP and GUI source trees now live as submodules under `eu5miner.mcp` and `eu5miner.gui` inside the single `eu5miner` wheel. Replace `from eu5miner_mcp.X import Y` with `from eu5miner.mcp.X import Y`, and `from eu5miner_gui.X import Y` with `from eu5miner.gui.X import Y`.
- The four console scripts (`eu5miner`, `eu5miner-mcp`, `eu5miner-gui`, `eu5miner-gui-shell`) now resolve from the unified wheel.
- `packages/mcp/` and `packages/gui/` source trees are removed. Tests moved under `packages/core/tests/{mcp,gui}/`.
- Removed workspace members in root `pyproject.toml` (the umbrella now has a single Python project).
- Display strings updated: `EU5MinerMCP` → `eu5miner-mcp`, `EU5MinerGUI` → `eu5miner-gui`, to match the new module paths.

### Migration

See [RENAMING.md](RENAMING.md).

---

## 0.7.0 — Workspace consolidation

EU5MinerMCP and EU5MinerGUI have been merged into this repository as a uv workspace. Three coordinated Python packages are now published from this single repo:

- `eu5miner` (unchanged) — core library and CLI
- `eu5miner-mcp` (was `EU5MinerMCP`) — MCP server
- `eu5miner-gui` (was `EU5MinerGUI`) — Kivy desktop UI

### Breaking changes
- Repository layout: see [README.md](README.md) for the new workspace structure.
- `pyproject.toml` moved to `packages/<name>/pyproject.toml` for each sub-package. The root `pyproject.toml` is workspace-only.
- The repo-root `__main__.py` is gone. Use `python -m eu5miner` (unchanged).
- Cross-package imports unchanged: `from eu5miner import ...` still works.
- Optional extras: `pip install eu5miner[mcp]`, `eu5miner[gui]`, `eu5miner[all]`.

### Migration
See [RENAMING.md](RENAMING.md).

---

## 0.6.x — Public preview

### 0.6.0 - 2026-04-06

- Added a substantially broader read-only inspection facade: downstream callers can now list supported entity-browsing systems, enumerate entities, and fetch detailed entities for the initial economy, diplomacy, government, religion, and map families.
- Locked the intended preview compatibility boundary with focused contract coverage for `eu5miner.inspection`, grouped domain packages, the thin CLI command surface, README examples, and the higher-level `eu5miner.mods` workflow.
- Added explicit `python -m eu5miner` and wheel `__main__` entrypoints so packaged CLI execution matches the documented thin command surface.
- Cleaned the default no-install validation baseline so `uv run pytest` stays warning-free even without optional plugins, and added release-readiness docs for the later `1.0` proposal.
- Refreshed README, roadmap, spec-index, scope, security, and environment wording so the checked-in preview state and OneDrive-safe `uv` workflow stay consistent across the repo.

### 0.5.0 - 2026-03-28

- First public preview release.
- Install discovery, virtual filesystem helpers, generic text-family parsing, and typed domain adapters are available from the published package.
- The CLI includes install inspection, representative parsing, system reporting, and the current mod update planning and application workflow.
- Representative-file tests, strict typing, and focused integration coverage are in place across the implemented parser and domain layers.
- API stabilization is still in progress ahead of a later `1.0` release.
