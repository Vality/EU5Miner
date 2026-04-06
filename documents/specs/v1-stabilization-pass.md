# V1 Stabilization Pass

## Objective

Prepare the current preview library seams for a deliberate `1.0` compatibility decision without widening scope or cutting the release as part of this pass.

This spec is about making the existing contract explicit, tightening validation around that contract, and removing ambiguity from docs and examples. It is not a promise to add broad new capability before `1.0`.

## Repo Scope

- `EU5Miner`

## No-Install Requirement

Most work under this spec should stay executable without a local EU5 install.

Primary validation remains the hosted-friendly baseline:

- `uv run pytest`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

Real-install validation is still recommended before a real `1.0` release is cut, but it should remain a targeted manual check over already-documented workflows instead of a prerequisite for every task in this pass.

## Current Status

Most of the first stabilization hardening work for this pass has already landed in the current preview line.

- focused compatibility coverage now locks the documented thin CLI mod workflow around mixed content inputs and stdout or stderr diagnostics
- focused compatibility coverage now locks the intended inspection-facing public seam, including supported-system metadata, browsable-system metadata, and the import boundary between the root package and `eu5miner.inspection`
- the remaining work is expected to stay narrow: release-readiness doc alignment, example truthfulness checks, and any final compatibility audits that uncover a concrete gap in the current curated contract

## Stabilization Criteria

Treat this pass as complete when all of the following are true:

- the intended `1.0` contract is explicit for the current curated seams: the root package, grouped domain packages, `eu5miner.inspection`, `eu5miner.mods`, and the thin CLI surface
- docs and examples consistently use the same preferred import paths and workflows
- higher-level tests cover the stable seams that docs tell downstream users to depend on
- preview-only convenience helpers, ambiguous import paths, or accidental exports are either documented as non-contract or removed from preferred documentation before release work begins
- the default validation loop stays install-independent and green

## Non-Goals

- adding major new parser families or broad new gameplay-domain coverage
- promising stability for every exported helper or internal implementation module
- expanding the CLI into a separate product surface beyond its current thin-wrapper role
- moving GUI or MCP product work back into the core repo
- introducing a full write-back engine or broader formatting-preserving editing scope
- creating release tags, version bumps, or distribution artifacts for `1.0`

## Likely Work Packages

### 1. Public Contract Audit

- review the root package and grouped domain package entrypoints against what the README and roadmap describe as stable
- confirm that `eu5miner.inspection` and `eu5miner.mods` remain the intended downstream-facing facades for high-level read-only and mod workflow use cases
- identify ambiguous exports, duplicated entrypoints, or examples that still imply a wider contract than the project intends to keep

### 2. Documentation And Example Alignment

- align `README.md`, `ROADMAP.md`, `documents/specs/README.md`, and `documents/v1-scope.md` around the same `1.0` boundary
- make the distinction clear between the current preview line, the intended `1.0` contract, and areas that are still intentionally out of scope
- keep examples anchored on the current architecture rather than describing future generic graph, writer, or product capabilities that do not exist yet
- prefer small truthfulness updates over broad rewrites; this stage should mostly remove ambiguity about what is already done versus what still blocks a real release proposal

### 3. Compatibility-Focused Validation

- add or tighten tests around the stable import seams and the high-level workflows they expose
- prefer tests that exercise public facades and grouped packages instead of internal modules
- expand synthetic workflow coverage where docs make compatibility claims, especially around inspection and mod planning or application flows
- treat this as follow-up work only when a verified contract gap remains; do not reopen already-landed hardening slices without a concrete mismatch to resolve

### 4. Release-Readiness Gate Definition

- define the blockers that must be cleared before an actual `1.0` release is proposed
- keep that gate narrow: explicit contract, aligned docs, stable validation, and targeted manual sanity checks on representative install-backed workflows
- treat downstream GUI and MCP consumption as coordination checks for release readiness, not as a reason to widen the core contract ad hoc
- keep the concrete gate grounded in current checked-in behavior; the current working definition lives in `documents/v1-release-readiness.md`

At the current stage, most tasks under this work package should be clarification or close-out tasks rather than new capability work.

## Acceptance Criteria

- one documented `1.0` boundary exists for the current architecture instead of several slightly different ones across docs
- public examples prefer the same curated seams that the roadmap and README describe
- validation covers the stable seams strongly enough that compatibility regressions are easier to catch than they are today
- no part of the spec requires reopening completed foundation work or promising unimplemented product scope
- the repo is positioned for a later `1.0` release proposal without that proposal being part of this spec

## Validation Expectations

Required baseline validation:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

Optional broader sweep:

```powershell
uv run python -m pytest -m broad
```

Recommended manual check before a real release proposal, when a local install is available:

- run the documented install inspection and system-report workflows against a representative local install
- run the current mod planning or application workflow against a small representative mod workspace
- confirm that downstream GUI and MCP work is still using the documented core seams instead of internal modules

## Notes For Agents

- Prefer narrow, compatibility-oriented tasks over large feature work.
- If a task needs a new public seam to justify itself, it likely belongs before or outside this stabilization pass.
- If a truthful `1.0` doc update would require new behavior, record that gap explicitly instead of promising it away in documentation.
