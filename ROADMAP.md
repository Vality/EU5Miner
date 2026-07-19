# Roadmap

## v0.8.x — Single-wheel consolidation
- [x] Merge `packages/mcp/` and `packages/gui/` into `packages/core/` as `eu5miner.mcp` and `eu5miner.gui` submodules.
- [x] Publish a single `eu5miner` wheel to PyPI with optional extras `[mcp]`, `[gui]`, `[all]`.
- [x] Drop the per-package `eu5miner-mcp` and `eu5miner-gui` PyPI distributions.

## v0.7.x — Workspace consolidation

- [x] Merge `EU5MinerMCP` and `EU5MinerGUI` into `Vality/EU5Miner` as a uv workspace
- [x] Three coordinated wheels: `eu5miner`, `eu5miner-mcp`, `eu5miner-gui`
- [x] Optional extras on `eu5miner`: `[mcp]`, `[gui]`, `[all]`
- [x] Archive `Vality/EU5MinerMCP` and `Vality/EU5MinerGUI`

## v0.6.x — Public preview line

The `0.6.x` line is the public preview baseline published from the three-repo workspace prior to consolidation. It included the core library seam expansion (`eu5miner.inspection`, `eu5miner.mods`), the narrow CLI surface, the MCP shell with install/file/system/mod-workflow tools and grouped-helper reports for diplomacy and religion, and the Kivy desktop GUI plus its read-only text-browser regression seam.

## Planning Model

The roadmap stays intentionally high level.

- `ROADMAP.md`: sequencing, release posture, and cross-package order of operations
- `documents/`: research, architecture, environment notes, and execution-ready spec material

## Release Posture

- `0.6.x` is the current public preview line (still supported on the core package and downstream extras).
- Patch releases are appropriate for validation fixes, packaging fixes, CI or automation changes, and refactors that do not add new user-facing capability.
- Minor releases should be reserved for a completed roadmap slice that changes what users can materially do with the library or downstream packages.

## Preview Posture

Downstream `packages/mcp/` and `packages/gui/` should treat the core library as their source of truth and remain thin product layers over the curated `eu5miner` seams.

- Downstream packages should prefer documented stable seams such as the root package, grouped domain packages, `eu5miner.inspection`, and `eu5miner.mods` instead of reaching into internal modules.
- If coordinated work needs a new seam, add or refine it deliberately in the core library first, then update GUI or MCP to consume it.
- Preview coordination does not make the whole core package a stable free-for-all API surface.

## Completed Preview Slices

1. Library integration and API polish baseline
2. Validation expansion baseline
3. Three-repo workspace and shared scaffolding baseline
4. First GUI foundation plus structured read-only browsing
5. First MCP foundation plus initial inspect, file, system, and mod workflow tools
6. Core preview hardening follow-up over the current stable seams
7. Core `1.0` stabilization close-out over the checked-in compatibility boundary

## Next Recommended Slices

### 1. Workspace Consolidation Close-Out (v0.7.x)

Status: complete for the current checked-in workspace state.

Goal: keep the new uv workspace, three coordinated wheels, and optional extras aligned without expanding scope.

Use this slice for:

- README, ROADMAP, CHANGELOG, and RENAMING truthfulness across the three sub-packages
- lockstep version bumps across `eu5miner`, `eu5miner-mcp`, and `eu5miner-gui`
- archived-repo notices and redirects

Do not use this slice to widen API or product surface during the consolidation window.

### 2. Core V1 Stabilization Pass

Status: complete for the previous checked-in core repo state; keep this slice as the reference boundary for later release work rather than reopening it for new feature scope.

Goal: turn the current preview seams into one explicit `1.0` compatibility boundary without broadening the architecture or cutting the release in this slice.

Use this slice for:

- final public-contract decisions on already-curated seams
- compatibility-focused tests around inspection and mod workflows
- documentation and example alignment around the intended `1.0` boundary
- release-readiness gates that stay grounded in current behavior

The remaining post-release work lives outside this slice: keep the automated gate green, run the documented manual install-backed sanity checks, and handle later patch or release decisions separately.

### 3. GUI Read-Only Browsing Refinement

Status: the first downstream breadth slice is already complete for the current checked-in repo state through the shipped Kivy desktop shell and the read-only text-browser regression seam.

Goal: keep future GUI follow-ons thin over the existing browser model rather than rebuild the shell.

Use this slice for:

- clearer browse flows around overview and report pages
- better presentation of partial-install and unavailable-report states
- thin GUI-side integration work that stays over `eu5miner.inspection`

### 4. MCP Server Contract Consolidation

Status: the first downstream breadth slice is already complete for the current checked-in repo state through the shipped grouped-helper tools for diplomacy and religion.

Goal: tighten the current tool surface before promising larger MCP scope.

Use this slice for:

- clearer tool descriptors and request or response shaping
- stronger separation between local shell behavior and transport work
- targeted additions only when backed by stable core seams

## Decision Rules

Use these rules when choosing the next task:

1. If the task affects stable imports, grouped package entrypoints, inspection helpers, or mod workflow seams, it belongs in `packages/core/`.
2. If the task is mostly contract clarification, synthetic tests, fixture design, or validation policy for existing seams, it belongs under the `1.0` stabilization pass in `packages/core/`.
3. If the task is about browse flow, report presentation, or install/session UX over existing library APIs, it belongs in `packages/gui/`.
4. If the task is about MCP tool contracts, server boundaries, or transport readiness over existing library APIs, it belongs in `packages/mcp/`.
5. If coordinated work needs a new downstream seam, land that seam in the core library first and only then consume it downstream.
