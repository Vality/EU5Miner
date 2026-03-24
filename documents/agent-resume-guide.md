# Agent Resume Guide

## Why This Exists

This document is meant to get a new Copilot or coding agent back to productive work quickly without having to rediscover the project structure, the research basis, or the local EU5 install layout.

## Repo Purpose

EU5Miner is a Python library for parsing Europa Universalis V data files for two adjacent use cases:

- data mining and indexing
- future mod creation and editing support

The project is intentionally text-first. Binary formats are deferred.

## Where To Read First

If you are resuming work, use this order:

1. `README.md` for the quick-start workflow
2. `documents/architecture.md` for layer boundaries
3. `documents/research-findings.md` for validated assumptions about the game and mod structure
4. `documents/data-type-roadmap.md` for the planned implementation order
5. `documents/testing-strategy.md` for the expected test discipline
6. `documents/development-environment.md` for the OneDrive and `uv` setup

## Current Source Tree

### Core package

- `src/eu5miner/paths.py`: finds the install root
- `src/eu5miner/source.py`: models the discovered install and representative sample files
- `src/eu5miner/vfs.py`: merges sources and tracks provenance
- `src/eu5miner/cli.py`: thin CLI wrappers around stable library behavior

### Generic format layers

- `src/eu5miner/formats/script_text.py`: structural script inspection helpers
- `src/eu5miner/formats/localization.py`: localization reader
- `src/eu5miner/formats/map_csv.py`: semicolon CSV reader
- `src/eu5miner/formats/metadata.py`: JSON metadata reader
- `src/eu5miner/formats/cst.py`: tokenizer and first-pass grouped CST for Clausewitz-style text
- `src/eu5miner/formats/semantic.py`: reusable semantic helpers on top of the CST

### Domain adapters

- `src/eu5miner/domains/scripted_triggers.py`
- `src/eu5miner/domains/scripted_effects.py`
- `src/eu5miner/domains/setup_countries.py`
- `src/eu5miner/domains/_macros.py`: shared macro parameter collection

### Tests

The most relevant regression suites are:

- `tests/test_cst.py`
- `tests/test_semantic.py`
- `tests/test_scripted_triggers.py`
- `tests/test_scripted_effects.py`
- `tests/test_setup_countries.py`
- `tests/test_cli.py`
- `tests/test_vfs.py`

Real-file coverage is preferred whenever new domain parsing is added.

## Validated Game Structure

The local install researched for this project is:

- `C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V`

Top-level structure observed there:

- `game`
- `jomini`
- `clausewitz`
- `binaries`
- `platform_specific_game_data`
- revision and branch marker files

Within `game/`, the important phase-aware structure is:

- `loading_screen`
- `main_menu`
- `in_game`
- `dlc`
- `mod`

Within `game/in_game/`, the currently relevant content families include:

- `common`
- `events`
- `gui`
- `map_data`
- `setup`

This phase split is important and should remain a first-class concept in the codebase.

## Representative Files Used In Research And Tests

- `game/in_game/events/readme.txt`
- `game/in_game/events/ages.txt`
- `game/in_game/events/civil_war.txt`
- `game/in_game/common/scripted_triggers/country_triggers.txt`
- `game/in_game/common/scripted_effects/country_effects.txt`
- `game/in_game/setup/countries/00_readme.info`
- `game/in_game/setup/countries/france.txt`
- `game/in_game/gui/agenda_view.gui`
- `game/in_game/map_data/default.map`
- `game/in_game/map_data/adjacencies.csv`
- `game/main_menu/localization/english/actions_l_english.yml`
- `game/dlc/D000_shared/D000_shared.dlc.json`

## Important Research Conclusions

- EU5 content is phase-loaded, so file resolution must understand `loading_screen`, `main_menu`, and `in_game`.
- The initial value is in text-based file families, not binary reverse engineering.
- Mods mirror the game structure under `game/`.
- `.metadata/metadata.json` matters for mod metadata.
- Database entry modes such as `INJECT:key` and `REPLACE:key` are important future work.
- Generated helper docs such as `script_docs` and `dump_data_types` are useful if present but cannot be required.

## Current State

Implemented and green:

- install discovery
- merged virtual filesystem
- generic text readers for localization, metadata, CSV, and script inspection
- CST tokenizer and grouped parser
- semantic helper layer
- CLI commands for install inspection and script analysis
- typed adapters for scripted triggers, scripted effects, and setup countries
- typed adapters for scripted triggers, scripted effects, setup countries, events, missions, situations, disasters, and localization helper families

Recently validated:

- setup-country color fields may be scalar values such as `map_FRA` or object-like prefixed blocks such as `rgb { ... }` and `hsv360 { ... }`
- parser-sensitive tests now run with timeouts so performance regressions fail quickly

## Next Planned Work

The next recommended domain target is `localization bundles and cross-reference helpers`.

The broader validation sweep is intentionally deferred for later and should stay optional rather than becoming part of the default fast development loop.

Real event structure confirmed during research and now covered by the first adapter:

- files usually begin with `namespace = ...`
- top-level event blocks are keyed like `namespace.1 = { ... }`
- common fields include `type`, `title`, `desc`, `trigger`, `immediate`, `after`, and repeated `option` blocks
- `game/in_game/events/readme.txt` describes the expected event schema and should anchor the first event adapter

## Environment And Commands

Because the repo is under OneDrive, the preferred environment is outside the repo:

- `%USERPROFILE%\.venvs\EU5Miner`

Bootstrap:

```powershell
.\scripts\setup-centralized-uv.ps1
```

Manual shell setup if needed:

```powershell
$env:UV_PROJECT_ENVIRONMENT = Join-Path $env:USERPROFILE '.venvs\EU5Miner'
```

Standard validation:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
```

If `uv run` ever touches the repo-local `.venv` and hits OneDrive permission issues, prefer the centralized environment rather than debugging the local environment.

## Practical Resume Workflow

1. Read `AGENTS.md` and this file.
2. Confirm the environment is pointing at `%USERPROFILE%\.venvs\EU5Miner`.
3. Run the focused tests for the area you are changing.
4. Read the relevant domain adapter and its tests before editing parser layers.
5. Only extend the generic CST or semantic layers when a new pattern is clearly reusable.
6. Update docs if the roadmap or operating assumptions change.
