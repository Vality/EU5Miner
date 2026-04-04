# Spec Index

These specs are the execution layer under `ROADMAP.md`.

Use them when creating issues or dispatching cloud agents.

## How To Use These Specs

Each spec should be actionable without a local EU5 install unless it explicitly says otherwise.

When handing work to an agent, copy:

1. the objective
2. the repo scope
3. the in-scope work items
4. the acceptance criteria
5. the validation commands

## Current Specs

- `library-integration-pass.md`: tighten the stable library surface and reduce cross-domain API drift
- `validation-expansion.md`: broaden confidence without requiring real-install access for most work
- `repo-topology-and-scaffolding.md`: standardize the three-repo workspace and shared repo structure
- `eu5miner-mcp-foundation.md`: first MCP repo foundation over the core library
- `eu5miner-gui-foundation.md`: first GUI repo foundation over the core library

## Agent Rules

- Prefer work that can validate with `pytest`, `ruff`, `mypy`, and `uv build` in CI.
- Treat real-install validation as a follow-up or explicit manual check unless the spec requires it.
- Do not widen public API seams casually; the integration-pass spec controls that work.