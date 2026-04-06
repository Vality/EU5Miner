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

Recent stabilization work has also landed for the documented thin CLI mod workflow: high-level compatibility coverage now locks mixed `--content-root`, `--content-file`, and `--intended-path` behavior plus the stdout report and stderr diagnostics split.

Recent stabilization work has also landed for the inspection-facing public seam: focused compatibility coverage now locks the supported-system ordering and descriptions, the curated browsable-entity ordering and descriptions, and the intended import split between the root package and `eu5miner.inspection`.

Recent stabilization work has also landed for the thin CLI surface: focused parser-contract and workflow-contract coverage now locks the documented command set, key option surface, and the intended stdout or stderr split for mod workflow diagnostics.

Use them in two ways:

- as reference when polishing or extending the shipped preview seams
- as a record of what is already complete, so new work does not restart foundation slices

That narrow close-out pass is now reflected in the checked-in core repo: docs, examples, and compatibility-focused tests align around the same curated `1.0` boundary. Remaining pre-release work is the later release step plus targeted manual install-backed sanity checks, not another round of core feature work.

That checked-in state also assumes the downstream preview repos have already completed their first narrow grouped-helper breadth through diplomacy and religion. The current cross-repo phase is operational rather than architectural: keep validation, build, test, and release-readiness work aligned across all three repos instead of reopening feature breadth.

## Current Core Reference Milestone

- `v1-stabilization-pass.md`: the reference milestone for the explicit `1.0` contract on the current architecture; use it to keep later release work grounded in the checked-in boundary rather than to reopen feature scope

The remaining focus under that milestone is now operational rather than architectural: keep the automated gate green and complete the documented manual checks before an actual release proposal.

For the step-3 coherence sweep across the three preview repos, use the roadmap, changelog, README, and release-readiness docs to keep status language truthful. Do not treat the core spec index as a prompt to start a new feature slice.

Do not use that milestone to recreate the already-landed CLI or inspection stabilization rounds unless a verified regression or contract ambiguity requires follow-up.

## Reference Specs For Ongoing Core Polish

- `library-integration-pass.md`: reference material for stable-surface cleanup and contract audits that started during preview hardening
- `validation-expansion.md`: reference material for synthetic coverage, validation discipline, and CI-safe hardening around existing seams

## Landed Baseline Specs

- `repo-topology-and-scaffolding.md`: the three-repo workspace and shared scaffolding baseline are in place
- `eu5miner-gui-foundation.md`: the downstream GUI foundation has landed in the dedicated repo
- `eu5miner-mcp-foundation.md`: the downstream MCP foundation has landed in the dedicated repo

The older core specs remain useful guardrails, but the stabilization pass is now the main planning entry for core work that is explicitly about the path to `1.0`.

In practice, that now means preserving the current truthfulness checks over behavior rather than starting another broad hardening phase.

## Agent Rules

- Prefer work that can validate with `pytest`, `ruff`, `mypy`, and `uv build` in CI.
- Treat real-install validation as a follow-up or explicit manual check unless the spec requires it.
- Do not widen public API seams casually; use the stabilization pass to clarify the intended contract and the older integration and validation specs as supporting guardrails.
- For downstream follow-on work, prefer the repo-local roadmap and spec docs in `EU5MinerGUI` or `EU5MinerMCP` instead of reopening completed foundation work here.
