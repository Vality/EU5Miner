# Spec: Validation Expansion

## Objective

Increase confidence in the preview line while keeping the default development loop fast and cloud-agent-friendly.

## Repo Scope

- `EU5Miner`

## No-Install Requirement

This spec is intentionally biased toward synthetic validation and CI-safe checks.

Real-install coverage can be expanded later, but most work under this spec should be possible without access to a shipped EU5 install.

## In Scope

- improve synthetic fixtures and reusable integration surfaces
- tighten CLI and facade-level test coverage where stable seams already exist
- refine `pytest -m broad` boundaries and test selection
- improve validation docs so agents know which checks are mandatory versus optional
- ensure CI stays green and useful for cloud work

## Out Of Scope

- install-specific content audits that require local game data for every task
- large new parser families
- product-layer GUI or MCP implementation

## Suggested Work Slices

1. Synthetic integration surfaces
   - expand reusable temp-path installs or mods for higher-level workflow tests
   - prefer fixtures that cover VFS, mods, and grouped helper layers together

2. Broad sweep definition
   - convert the broad sweep into a more intentionally selected regression layer
   - keep it optional by default

3. CI validation discipline
   - keep required CI checks aligned with what can pass in a hosted environment
   - avoid making real-install access a requirement for baseline CI

4. Failure triage clarity
   - keep docs explicit about what failures mean and which validation tier they belong to

## Acceptance Criteria

- the default validation loop remains install-independent
- the optional broad sweep is better defined than it is today
- higher-level synthetic workflows cover more of the stable library surface
- CI remains a reliable gate for cloud-agent work

## Validation

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

The final command remains optional for most cloud-agent tasks.