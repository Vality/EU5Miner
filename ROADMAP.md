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
- the recent preview hardening follow-up over the already-curated library seams
- a completed core `1.0` stabilization close-out over public-contract docs, example truthfulness, and compatibility-focused CLI and inspection coverage
- a completed stabilization hardening slice for the thin CLI mod workflow contract around mixed intended or content inputs and stdout or stderr diagnostics
- a completed stabilization hardening slice for inspection-facing compatibility coverage and explicit import-boundary locking around `eu5miner.inspection` versus root imports
- install discovery, merged VFS support, CST and semantic parsing helpers, and broad typed domain coverage in the core library
- a stable read-only inspection facade and thin CLI over the intended library seams
- initial mod planning and apply workflows in the core library
- a structured read-only browser model in `EU5MinerGUI`
- thin grouped-helper GUI pages for diplomacy and religion in `EU5MinerGUI`
- a typed MCP shell in `EU5MinerMCP` with `inspect-install`, `list-files`, `list-systems`, `report-system`, `plan-mod-update`, and `apply-mod-update`
- thin grouped-helper MCP tools for diplomacy and religion in `EU5MinerMCP`

The next work should build on those shipped seams instead of repeating foundation or repo-setup slices.

The checked-in three-repo state now covers the completed core step-1 stabilization boundary and the completed downstream step-2 grouped-helper breadth through diplomacy and religion. The immediate step-3 follow-on is coherence and release execution discipline: keep docs truthful, run the full validation and build gate, and align release-readiness work across the three preview repos.

For the checked-in core repo state, the stabilization close-out is now effectively complete. Remaining work before proposing an actual `1.0` release is the later release step plus the targeted manual install-backed sanity checks documented in `documents/v1-release-readiness.md`.

## Completed Preview Slices

1. Library integration and API polish baseline
2. Validation expansion baseline
3. Three-repo workspace and shared scaffolding baseline
4. First GUI foundation plus structured read-only browsing
5. First MCP foundation plus initial inspect, file, system, and mod workflow tools
6. Core preview hardening follow-up over the current stable seams
7. Core `1.0` stabilization close-out over the checked-in compatibility boundary

## Next Recommended Slices

### 1. Core V1 Stabilization Pass

Status: complete for the current checked-in core repo state; keep this slice as the reference boundary for later release work rather than reopening it for new feature scope.

Goal: turn the current preview seams into one explicit `1.0` compatibility boundary without broadening the architecture or cutting the release in this slice.

Use this slice for:

- final public-contract decisions on already-curated seams
- compatibility-focused tests around inspection and mod workflows
- documentation and example alignment around the intended `1.0` boundary
- release-readiness gates that stay grounded in current behavior

Reference spec:

- `documents/specs/v1-stabilization-pass.md`

The earlier integration and validation specs remain useful reference material for follow-up polish, but they are no longer the primary milestone definition.

The checked-in repo now reflects that release-readiness alignment and compatibility-audit work. The remaining release-readiness work lives outside this slice: keep the automated gate green, run the documented manual install-backed sanity checks, and handle the eventual version bump and release execution separately.

Treat this as a close-out pass on the current preview contract, not as a new feature phase. If a proposed task needs a broader API or new capability to justify itself, it does not belong in this slice.

### 2. GUI Read-Only Browsing Refinement

Status: the first downstream breadth slice is already complete for the current checked-in repo state through the shipped diplomacy and religion helper pages.

Goal: keep future GUI follow-ons thin over the existing browser model rather than rebuild the shell.

Use this slice for:

- clearer browse flows around overview and report pages
- better presentation of partial-install and unavailable-report states
- thin GUI-side integration work that stays over `eu5miner.inspection`

Do not treat this as the current next major phase while cross-repo validation, build, test, and release-readiness work is still open.

### 3. MCP Server Contract Consolidation

Status: the first downstream breadth slice is already complete for the current checked-in repo state through the shipped diplomacy and religion helper tools.

Goal: tighten the current tool surface before promising larger MCP scope.

Use this slice for:

- clearer tool descriptors and request or response shaping
- stronger separation between local shell behavior and future transport work
- targeted additions only when backed by stable core seams

Do not treat this as the current next major phase while cross-repo validation, build, test, and release-readiness work is still open.

### 4. Cross-Repo Validation, Build, Test, And Preview Release Alignment

Goal: keep the three preview repos aligned now that the core step-1 close-out and the first downstream step-2 breadth slices are both checked in.

Use this slice for:

 - full validation, type-check, lint, and build execution in each repo
 - dependency and changelog alignment
 - roadmap and README consistency across repos
 - release-ready validation, manual sanity-check planning, and documentation polish

## Decision Rules

Use these rules when choosing the next task:

1. If the task affects stable imports, grouped package entrypoints, inspection helpers, or mod workflow seams, it belongs in the core repo.
2. If the task is mostly contract clarification, synthetic tests, fixture design, or validation policy for existing seams, it belongs under the `1.0` stabilization pass in the core repo.
3. If the task is about browse flow, report presentation, or install/session UX over existing library APIs, it belongs in the GUI repo.
4. If the task is about MCP tool contracts, server boundaries, or transport readiness over existing library APIs, it belongs in the MCP repo.
5. If coordinated work needs a new downstream seam, land that seam in the core library first and only then consume it downstream.

## Current Recommendation

The immediate sequence should be:

1. treat the current foundation specs as completed baseline and reference material
2. treat the core stabilization pass as completed reference material for the intended `1.0` contract on the current curated seams
3. treat the downstream diplomacy and religion grouped-helper slices as completed reference material rather than the next active feature phase
4. use the step-3 coherence sweep to keep README, roadmap, changelog, and spec-index wording aligned across repos
5. make full validation, build, test, and targeted manual sanity checks the next major phase before proposing an actual `1.0` cut
