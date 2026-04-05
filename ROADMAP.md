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
- `documents/specs/`: execution-ready work packages for agents and contributors
- `documents/architecture.md`: design constraints and layering rules
- `documents/development-environment.md`: local environment notes and validation commands

## Release Posture

- `0.5.x` is a preview line.
- Patch releases are appropriate for validation fixes, packaging fixes, CI or automation changes, and refactors that do not add new user-facing capability.
- Minor releases should be reserved for a completed roadmap slice that changes what users can materially do with the library or downstream products.

## Preview Downstream Dependency Posture

During the preview phase, the downstream `EU5MinerGUI` and `EU5MinerMCP` repos should treat the core library as their source of truth and should remain thin product layers over the curated `eu5miner` seams.

- For bootstrap CI and coordinated preview work, the default downstream dependency posture is to consume `eu5miner` from the GitHub `main` branch until packaged releases exist.
- That temporary dependency posture does not make `main` a stable free-for-all API surface; parser, VFS, and domain-model logic still belong in the core repo.
- Downstream repos should prefer the documented stable seams such as the root package, grouped domain packages, and other explicitly curated entrypoints instead of reaching into internal modules.
- If coordinated work across repos needs a new seam, add or refine it deliberately in the core library first, then update GUI or MCP to consume it. Do not widen the downstream stable boundary casually just because all three repos are moving together.

## Baseline

The core library now has:

- install discovery and merged VFS support
- CST and semantic parsing helpers
- broad typed domain adapter coverage
- a thin CLI over the stable library seams
- initial mod planning and apply workflows
- CI, Dependabot, and cloud-agent scaffolding

That means the next highest-value work is no longer "add another parser family by default". It is to stabilize the integrated surface and then use it from downstream products.

## Roadmap Order

### 1. Library Integration And API Polish

Goal: tighten the curated library surface so downstream repos can depend on it with confidence.

When to do this:

- before substantial MCP or GUI feature work
- before another minor version bump

Spec:

- `documents/specs/library-integration-pass.md`

### 2. Validation Expansion And Hardening

Goal: make the preview line more reliable without forcing cloud agents to need a local EU5 install.

When to do this:

- immediately after or alongside the integration pass
- before widening downstream automation

Spec:

- `documents/specs/validation-expansion.md`

### 3. Multi-Repo Workspace Alignment

Goal: standardize the library, GUI, and MCP repos so work can be split safely across cloud agents.

When to do this:

- after the current documentation and planning model is in place
- before large parallel issue dispatch across repos

Spec:

- `documents/specs/repo-topology-and-scaffolding.md`

### 4. MCP Product Foundation

Goal: build the first read-only MCP service as a thin adapter over stable library APIs.

When to do this:

- after the library integration pass has identified the stable seams
- in the dedicated MCP repo, not inside the core library package

Spec:

- `documents/specs/eu5miner-mcp-foundation.md`

### 5. GUI Product Foundation

Goal: build the first read-only GUI shell for browsing parsed data and system reports.

When to do this:

- after the library integration pass has stabilized grouped package entrypoints and helper reports
- in the dedicated GUI repo, not inside the core library package

Spec:

- `documents/specs/eu5miner-gui-foundation.md`

## Decision Rules

Use these rules when choosing the next task:

1. If the task affects stable imports, grouped package entrypoints, or helper naming, it belongs under the library integration pass.
2. If the task is mostly synthetic tests, fixture design, CI, or validation policy, it belongs under validation expansion.
3. If the task is repo scaffolding, workspace structure, or shared automation, it belongs under multi-repo alignment.
4. If the task needs an install-backed product surface or user interface, it should happen in MCP or GUI only after the library surface is stable enough.

## Current Recommendation

The immediate sequence should be:

1. finish the documentation/spec refactor so planning stops being split across multiple legacy files
2. complete the library integration pass and API polish
3. expand validation in a cloud-agent-friendly way
4. stand up the three-repo workspace and shared repo scaffolding
5. start the first MCP and GUI foundation slices in parallel