# Spec: Library Integration Pass

## Objective

Stabilize the integrated library surface so downstream repos can depend on the core package without chasing avoidable API churn.

## Repo Scope

- `EU5Miner`

## No-Install Requirement

This spec is designed to be executable without a local EU5 install.

Primary validation is:

- `uv run pytest`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

Real-install checks are optional follow-up, not a blocker for most work items here.

## In Scope

- review the curated export surface in `src/eu5miner/__init__.py`
- review grouped package entrypoints under `src/eu5miner/domains/`
- align helper naming patterns across diplomacy, economy, government, religion, localization, map, and units
- reduce obvious duplication in cross-domain helper layers where naming or behavior drift has accumulated
- tighten README and CLI examples so they use the intended stable seams
- document what is stable enough for downstream repos to depend on

## Out Of Scope

- adding entirely new parser families by default
- MCP transport implementation
- GUI framework implementation
- large write-back or formatting-preserving writer work

## Suggested Work Slices

1. Export surface audit
   - compare root exports, grouped package exports, and internal helper modules
   - remove accidental duplication where one import path is clearly preferred

2. Naming review
   - ensure similar helper patterns use similar names and return shapes
   - prefer predictable pairs like `build_*_catalog`, `build_*_report`, `parse_*_document`

3. Downstream dependency boundary
   - identify which seams GUI and MCP should consume first
   - avoid exposing low-value internals just to make one downstream use case easier

4. Docs alignment
   - ensure README, AGENTS, and roadmap/spec docs all point at the same stable seams

## Acceptance Criteria

- stable seams are clearer than they are today
- grouped package entrypoints are internally consistent
- public examples use the same preferred import surfaces described in docs
- validation commands are green without requiring a game install

## Validation

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```