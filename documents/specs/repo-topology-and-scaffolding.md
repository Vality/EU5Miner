# Spec: Three-Repo Workspace And Shared Scaffolding

## Objective

Reshape the working setup into a coordinated three-repo workspace:

- `EU5Miner`
- `EU5MinerGUI`
- `EU5MinerMCP`

The goal is parallel development with cloud agents, consistent CI or Dependabot behavior, and matching docs structure across repos.

## Repo Scope

- `EU5Miner`
- `EU5MinerGUI`
- `EU5MinerMCP`

## In Scope

- clone or initialize the GUI and MCP repos locally as siblings of the library repo
- create a multi-root workspace file covering all three repos
- standardize baseline repo structure where appropriate:
  - `README.md`
  - `AGENTS.md`
  - `ROADMAP.md`
  - `documents/`
  - `documents/specs/`
  - `.github/`
  - `src/`
  - `tests/`
  - `pyproject.toml`
  - `.gitignore`
- align CI, Dependabot, and Copilot or agent instruction files across repos

## Out Of Scope

- fully implementing MCP or GUI product features
- forcing all three repos to share identical content where the product goals differ

## Shared Rules

- use the same Python build system and validation shape across repos
- keep repo-specific docs and specs, not one giant shared document copied verbatim everywhere
- let each repo depend on the library through a clear package dependency while preserving local parallel development
- during the preview phase, let GUI and MCP bootstrap CI against `eu5miner` from the GitHub `main` branch until packaged releases exist
- treat that dependency as a coordination mechanism, not as license to consume internal parser, VFS, or domain modules directly
- when coordinated work needs a new downstream seam, land the core-library API change first and then consume it from thin GUI or MCP adapters instead of widening the stable boundary ad hoc

## Expected Deliverables

1. local three-repo workspace file
2. baseline Python app skeleton in GUI repo
3. baseline Python app skeleton in MCP repo
4. shared automation shape across all repos
5. repo-local roadmap and specs in all three repos

## Acceptance Criteria

- each repo can run its own baseline validation in CI
- each repo has clear agent-facing docs and a roadmap/spec split
- the workspace structure supports parallel issue dispatch across repos
- the preview-phase downstream dependency posture is explicit enough that coordinated multi-repo work does not rely on undocumented stable seams