# Spec: EU5Miner GUI Foundation

## Objective

Create the initial GUI repo as a Python application that depends on the core library and provides a read-only shell for future data browsing.

## Repo Scope

- `EU5MinerGUI`

## No-Install Requirement

The first GUI foundation should not require a local EU5 install.

The repo should validate through smoke tests, import tests, and basic command or app bootstrap checks.

## In Scope

- Python package skeleton and app entrypoint
- dependency on the core `eu5miner` library
- a minimal launchable application shell
- smoke tests for package import and startup
- repo docs and automation aligned with the library repo

## Initial Package Shape

```text
src/
  eu5miner_gui/
    __init__.py
    app.py
    cli.py
```

The first implementation can stay intentionally thin. The point is to establish repo structure and validation, not to choose the full GUI stack immediately.

## First Milestone

- app entrypoint launches a placeholder shell or startup message
- package imports cleanly
- CI validates the repo without needing real game data

## Acceptance Criteria

- repo scaffolding is complete
- the package depends on the library cleanly
- the repo is ready for issue-driven cloud-agent work
