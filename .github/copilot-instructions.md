# Copilot Instructions

Use this repository as a typed, test-backed Python library first.

## Read First

Start with:

1. `README.md`
2. `AGENTS.md`
3. `ROADMAP.md`
4. `documents/specs/README.md`
5. `documents/development-environment.md`

## Working Norms

- Preserve the project layering: install and source discovery, VFS, generic format readers, semantic parsing, then domain adapters.
- Do not push EU5-specific behavior into the CST or semantic layers unless it is genuinely reusable.
- Prefer small, typed, test-backed changes.
- Keep helper layers above the parser families they compose.
- Treat `src/eu5miner/domains/__init__.py` as the curated public surface.
- Grouped package entrypoints such as `eu5miner.domains.diplomacy`, `...economy`, `...government`, `...religion`, `...map`, `...localization`, and `...units` are intended for concept-local imports.

## Validation

Run these required baseline checks before closing substantial work:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

Notes:

- The optional broader install sweep lives behind `uv run python -m pytest -m broad`.
- Real-file validation against a local EU5 install is preferred whenever a new domain or helper layer is introduced.
- Most roadmap and spec work should remain executable without a local EU5 install unless the spec explicitly requires one.

## Release Posture

- The current public line is a preview release, not a frozen `1.0` API.
- Root package imports, grouped domain packages, and `eu5miner.mods` are the main public seams to preserve.
- MCP and GUI work should stay outside the core `eu5miner` package until they are ready to become separate packages.
