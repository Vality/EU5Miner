# EU5Miner Roadmap

This roadmap is the top-level planning document for the EU5Miner family of repositories.

Use it to decide:

- what order major work should happen in
- when a release bump is justified
- when a task should stay in the library repo versus move to GUI or MCP

Detailed implementation guidance lives in `documents/specs/`.

## Planning Model

The roadmap stays intentionally high level.

- `ROADMAP.md`: sequencing, release posture, and cross-repo order of operations
- `documents/specs/`: execution-ready work packages and reference specs
- `documents/architecture.md`: design constraints and layering rules
- `documents/development-environment.md`: local environment notes and validation commands

## Release Posture

- `0.5.x` is a preview line.
- Patch releases are appropriate for validation fixes, packaging fixes, CI or automation changes, and refactors that do not add new user-facing capability.
- Minor releases should be reserved for a completed roadmap slice that changes what users can materially do with the library or downstream products.

## Preview Downstream Dependency Posture

During the preview phase, the downstream `EU5MinerGUI` and `EU5MinerMCP` repos should treat the core library as their source of truth and should remain thin product layers over the curated `eu5miner` seams.

- Downstream repos should prefer documented stable seams such as the root package, grouped domain packages, `eu5miner.inspection`, and `eu5miner.mods` instead of reaching into internal modules.
- If coordinated work across repos needs a new seam, add or refine it deliberately in the core library first, then update GUI or MCP to consume it.
- Preview coordination across repos does not make the whole core package a stable free-for-all API surface.

## Current Baseline

The completed preview baseline now includes:

- the core integration pass, validation expansion, and three-repo alignment work
- install discovery, merged VFS support, CST and semantic parsing helpers, and broad typed domain coverage in the core library
- a stable read-only inspection facade and thin CLI over the intended library seams
- initial mod planning and apply workflows in the core library
- a structured read-only browser model in `EU5MinerGUI`
- a typed MCP shell in `EU5MinerMCP` with `inspect-install`, `list-files`, `list-systems`, `report-system`, `plan-mod-update`, and `apply-mod-update`

The next work should build on those shipped seams instead of repeating foundation or repo-setup slices.

## Completed Preview Slices

1. Library integration and API polish baseline
2. Validation expansion baseline
3. Three-repo workspace and shared scaffolding baseline
4. First GUI foundation plus structured read-only browsing
5. First MCP foundation plus initial inspect, file, system, and mod workflow tools

## Next Recommended Slices

### 1. Core Preview Hardening From Downstream Usage

Goal: use real downstream consumption in GUI and MCP to tighten the preview library surface, docs, examples, and synthetic validation where rough edges still show.

Use this slice for:

- targeted API polish on already-curated seams
- higher-level tests around inspection and mod workflows
- documentation updates that keep the stable surface explicit

Reference specs:

- `documents/specs/library-integration-pass.md`
- `documents/specs/validation-expansion.md`

### 2. GUI Read-Only Browsing Refinement

Goal: iterate on the existing browser model rather than rebuild the shell.

Use this slice for:

- clearer browse flows around overview and report pages
- better presentation of partial-install and unavailable-report states
- thin GUI-side integration work that stays over `eu5miner.inspection`

### 3. MCP Server Contract Consolidation

Goal: tighten the current tool surface before promising larger MCP scope.

Use this slice for:

- clearer tool descriptors and request or response shaping
- stronger separation between local shell behavior and future transport work
- targeted additions only when backed by stable core seams

### 4. Cross-Repo Preview Release Alignment

Goal: keep the three preview repos aligned as the next release is cut.

Use this slice for:

- dependency and changelog alignment
- roadmap and README consistency across repos
- release-ready validation and documentation polish

## Decision Rules

Use these rules when choosing the next task:

1. If the task affects stable imports, grouped package entrypoints, inspection helpers, or mod workflow seams, it belongs in the core repo.
2. If the task is mostly synthetic tests, fixture design, or validation policy for existing seams, it belongs under preview hardening in the core repo.
3. If the task is about browse flow, report presentation, or install/session UX over existing library APIs, it belongs in the GUI repo.
4. If the task is about MCP tool contracts, server boundaries, or transport readiness over existing library APIs, it belongs in the MCP repo.
5. If coordinated work needs a new downstream seam, land that seam in the core library first and only then consume it downstream.

## Current Recommendation

The immediate sequence should be:

1. treat the current foundation specs as completed baseline and reference material
2. use downstream usage to harden the preview library surface and release docs
3. scope one focused GUI browse-refinement slice
4. scope one focused MCP contract-consolidation slice
5. cut the next preview release only after the cross-repo docs and dependency posture are aligned
