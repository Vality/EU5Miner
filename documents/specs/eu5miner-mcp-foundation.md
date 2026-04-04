# Spec: EU5Miner MCP Foundation

## Objective

Create the initial MCP repo as a Python application that depends on the core library and exposes a thin, typed server foundation.

## Repo Scope

- `EU5MinerMCP`

## No-Install Requirement

The initial repo foundation should be buildable and testable without a local EU5 install.

Use synthetic fixtures and smoke tests for the first milestones.

## In Scope

- Python package skeleton and console entrypoint
- dependency on the core `eu5miner` library
- basic server bootstrap module
- placeholder tool modules organized by concern
- smoke tests for importability and command startup
- repo docs and automation aligned with the library repo

## Initial Package Shape

```text
src/
  eu5miner_mcp/
    __init__.py
    cli.py
    server.py
    serializers.py
    tools/
      __init__.py
      install.py
      files.py
      entities.py
      systems.py
```

## First Milestone

- server process can start and print a minimal help or startup message
- package imports cleanly
- repo CI runs the same basic validation pattern as the library repo

## Acceptance Criteria

- repo scaffolding is complete
- package depends on the library cleanly
- no real install is required for the initial smoke tests