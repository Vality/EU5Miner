# EU5Miner Agent Guide

## Purpose

This repository is building a text-first Python library for reading, indexing, and later editing Europa Universalis V data and mod files.

Agents working here should optimize for:

- real-file validation against a local EU5 install
- minimal, typed, test-backed increments
- preserving the generic parser layers while adding domain-specific adapters on top

## Start Here

Read these documents first:

1. `README.md`
2. `ROADMAP.md`
3. `documents/specs/README.md`
4. `documents/architecture.md`
5. `documents/development-environment.md`

## Project Layout

- `src/eu5miner/paths.py`: install path resolution
- `src/eu5miner/source.py`: discovered EU5 install model and representative files
- `src/eu5miner/vfs.py`: merged virtual filesystem and provenance
- `src/eu5miner/formats/`: generic file-family readers and parser layers
- `src/eu5miner/domains/`: typed adapters for specific EU5 data families
- `tests/`: real-file and inline regression coverage
- `documents/`: research, architecture, roadmap, and environment notes
- `scripts/setup-centralized-uv.ps1`: OneDrive-safe `uv` environment bootstrap

## Current Parser Stack

The intended layering is:

1. install/source discovery
2. virtual filesystem merging
3. generic text-family readers
4. CST parser for Clausewitz-style text
5. semantic object/value helpers
6. domain adapters for concrete EU5 systems

Do not push EU5-specific behavior down into the CST or semantic layers unless the behavior is truly generic.

The roadmap also includes a later simple GUI viewer for convenient data inspection in addition to the CLI, but it should be built on top of stable library APIs rather than driving parser or domain design early.

Generated helper outputs such as `script_docs` and `dump_data_types` are useful optional inputs for schema discovery and later validation or viewer work, but they must stay optional. Prefer local debug-mode dumps when available because they match the installed build; use the public `modding-digests` mirror as a fallback reference.

The VFS now also has an initial metadata-aware replace-path layer: source metadata can contribute normalized `replace_path` rules, merged file views hide lower-priority files inside replaced subtrees, write-planning helpers cover both exact files and subtree summaries, an action-oriented layer can classify visible subtree entries as keep, override, or blocked while recommending when a subtree should add its own `replace_path`, an emission planner can include intended file paths that do not exist yet so callers can distinguish create, override, and blocked outcomes, a mod-oriented wrapper can group those file emissions with metadata updates such as adding `replace_path` entries, the first mod skeleton planner can derive required directories, metadata.json handling, and intended content-file paths from that mod emission plan, targeted emission helpers can render deterministic metadata.json and content-file write payloads from those plans, filesystem materialization helpers can create the planned directories and write those explicit metadata/content payloads with controlled overwrite behavior, a public `eu5miner.mods` facade now wraps that stack into stable plan/apply/report workflow helpers, and the CLI now exposes thin mod workflow commands for dry-run planning and application with advisories, warnings, and explicit content inputs.

## Implemented Domains

- scripted triggers
- scripted effects
- script values
- scripted modifiers
- scripted lists and scripted relations
- on_actions and related hook definitions
- building types and building categories
- goods, prices, and goods demand
- production methods and employment systems
- generic actions, first anchored on market and employment-system action files
- attribute columns, first anchored on default, market, and goods column files
- remaining trade and loan economy files validated through those same adapters
- casus belli and wargoals
- peace treaties and war-flow helper links
- subject types and subject military stances
- country interactions and character interactions
- diplomacy graph/report helpers over parsed war and interaction links
- unit types, unit abilities, and unit categories
- government types and government reforms
- laws and policies
- estates and estate privileges
- parliament types, agendas, and issues
- higher-level government helper layer over those connected families
- institutions, holy site types, holy sites, and a holy-site catalog helper
- societal values, religious aspects, religious factions, religious focuses, religious schools, and religious figures
- higher-level religion helper layer over those connected families
- setup countries
- cultures and culture groups
- religions and religion groups
- country description categories and related setup helpers
- events
- missions
- situations
- disasters
- customizable localization and effect/trigger localization helpers
- localization bundles and cross-reference helpers
- GUI script and scripted GUI
- loading screen and main menu content helpers
- map text files such as `default.map`
- map CSV helpers such as adjacencies and ports
- location/setup cross-linking helpers
- mod metadata and relationships

The current planning entrypoint is `ROADMAP.md`, with execution-ready work packages under `documents/specs/`.

Current recommended focus:

- complete the library integration pass before large downstream product work
- widen validation in cloud-agent-friendly ways that do not require a local game install by default
- keep MCP and GUI implementation in their own repos once the three-repo workspace is in place

The optional broader validation sweep now lives behind `uv run python -m pytest -m broad`; keep it out of the normal fast iteration loop.

## EU5 Install Facts

Install discovery and phase/layout assumptions live in `src/eu5miner/source.py`.

Representative sample selection should be maintained in `GameInstall.representative_files()` rather than copied into static docs.

Real-file validation should use locally available shipped content or optional generated dumps, but shipped game files, local profile artifacts, and generated dumps should not be committed to the repository.

## Environment Notes

This repo lives in a OneDrive-backed directory. Prefer the centralized `uv` environment:

- `%USERPROFILE%\.venvs\EU5Miner`

Bootstrap with:

```powershell
.\scripts\setup-centralized-uv.ps1
```

When running commands manually in a fresh shell, set:

```powershell
$env:UV_PROJECT_ENVIRONMENT = Join-Path $env:USERPROFILE '.venvs\EU5Miner'
```

## Validation Commands

Use these required baseline checks before closing substantial work:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

Run the broader optional sweep explicitly when you need wider install-backed coverage:

```powershell
uv run python -m pytest -m broad
```

For focused domain work, run the relevant test module first.

## Working Style

- prefer small, test-backed additions
- test against real EU5 files whenever a new domain is introduced
- preserve formatting-sensitive behavior in generic parsers
- fix root causes instead of layering ad hoc special cases
- update docs when the roadmap, environment, or project shape materially changes
