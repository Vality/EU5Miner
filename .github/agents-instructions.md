# Agent Instructions

This file applies to any agentic coding tool working in this repository:
Claude Code, GitHub Copilot, Hermes, or any other assistant. It is not
specific to a single vendor.

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

```bash
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

Notes:

- The optional broader install sweep lives behind `uv run python -m pytest -m broad`.
- Real-file validation against a local EU5 install is preferred whenever a new domain or helper layer is introduced.
- Most roadmap and spec work should remain executable without a local EU5 install unless the spec explicitly requires one.
- On Windows, the OneDrive-backed workspace needs `UV_LINK_MODE=copy` exported before `uv build`; see `documents/development-environment.md`.

## Release Posture

- The current public line is a preview release, not a frozen `1.0` API.
- Root package imports, grouped domain packages, and `eu5miner.mods` are the main public seams to preserve.
- MCP and GUI work should stay outside the core `eu5miner` package until they are ready to become separate packages.

## Tool-Specific Notes

- **Claude Code**: this file is auto-loaded when present. `AGENTS.md` is also recognized as a project-level instruction file.
- **GitHub Copilot**: this file is loaded by Copilot Coding Agent. `AGENTS.md` may also be picked up depending on the IDE.
- **Hermes**: this file is loaded by `hermes` when working in the repo directory. `AGENTS.md` is read for cross-agent conventions.
