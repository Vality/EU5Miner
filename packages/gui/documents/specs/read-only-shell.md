# Spec: Read-Only GUI Shell

## Objective

Create the first launchable GUI shell for the repo.

## In Scope

- app entrypoint
- placeholder shell or startup message
- smoke tests for launch behavior
- wiring to at least one stable import from `eu5miner`

## Out Of Scope

- editor workflows
- bespoke parser logic
- install-backed browsing that requires real game data

## Acceptance Criteria

- the app launches cleanly
- the repo validates in hosted CI
- the shell proves the dependency on the core library
