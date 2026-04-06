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

## Current Status

Most top-level specs in this folder now describe work that has already landed as the preview baseline or the recently completed preview hardening follow-up.

Use them in two ways:

- as reference when polishing or extending the shipped preview seams
- as a record of what is already complete, so new work does not restart foundation slices

## Next Core Milestone

- `v1-stabilization-pass.md`: the next major core milestone; use it to define the explicit `1.0` contract on the current architecture without treating the spec itself as release execution

## Reference Specs For Ongoing Core Polish

- `library-integration-pass.md`: reference material for stable-surface cleanup and contract audits that started during preview hardening
- `validation-expansion.md`: reference material for synthetic coverage, validation discipline, and CI-safe hardening around existing seams

## Landed Baseline Specs

- `repo-topology-and-scaffolding.md`: the three-repo workspace and shared scaffolding baseline are in place
- `eu5miner-gui-foundation.md`: the downstream GUI foundation has landed in the dedicated repo
- `eu5miner-mcp-foundation.md`: the downstream MCP foundation has landed in the dedicated repo

The older core specs remain useful guardrails, but the stabilization pass is now the main planning entry for core work that is explicitly about the path to `1.0`.

## Agent Rules

- Prefer work that can validate with `pytest`, `ruff`, `mypy`, and `uv build` in CI.
- Treat real-install validation as a follow-up or explicit manual check unless the spec requires it.
- Do not widen public API seams casually; use the stabilization pass to clarify the intended contract and the older integration and validation specs as supporting guardrails.
- For downstream follow-on work, prefer the repo-local roadmap and spec docs in `EU5MinerGUI` or `EU5MinerMCP` instead of reopening completed foundation work here.
