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
2. `documents/agent-resume-guide.md`
3. `documents/architecture.md`
4. `documents/data-type-roadmap.md`
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

The VFS now also has an initial metadata-aware replace-path layer: source metadata can contribute normalized `replace_path` rules, merged file views hide lower-priority files inside replaced subtrees, write-planning helpers cover both exact files and subtree summaries, an action-oriented layer can classify visible subtree entries as keep, override, or blocked while recommending when a subtree should add its own `replace_path`, an emission planner can include intended file paths that do not exist yet so callers can distinguish create, override, and blocked outcomes, a mod-oriented wrapper can group those file emissions with metadata updates such as adding `replace_path` entries, and the first mod skeleton planner can now derive required directories, metadata.json handling, and intended content-file paths from that mod emission plan.

## Implemented Domains

- scripted triggers
- scripted effects
- setup countries
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

Next planned target:

- targeted emission helpers

The optional broader validation sweep remains deferred until later; do not fold it into normal fast iteration work.

## EU5 Install Facts

The local research target used so far is:

- `C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V`

Important layout facts:

- top level contains `game`, `jomini`, `clausewitz`, and engine/version marker files
- `game/` contains `loading_screen`, `main_menu`, `in_game`, `dlc`, and `mod`
- most high-value moddable content currently targeted by this repo lives under `game/in_game/`

Important representative files:

- `game/in_game/events/readme.txt`
- `game/in_game/common/scripted_triggers/country_triggers.txt`
- `game/in_game/common/scripted_effects/country_effects.txt`
- `game/in_game/setup/countries/00_readme.info`
- `game/in_game/setup/countries/france.txt`
- `game/in_game/gui/agenda_view.gui`
- `game/in_game/gui/eventwindow.gui`
- `game/in_game/gui/ui_library.gui`
- `game/main_menu/common/scenarios/00_scenarios.txt`
- `game/loading_screen/localization/english/load_tips_l_english.yml`
- `game/in_game/map_data/default.map`
- `game/in_game/map_data/definitions.txt`
- `game/in_game/map_data/adjacencies.csv`
- `game/in_game/map_data/ports.csv`
- `game/main_menu/setup/start/10_countries.txt`
- `game/main_menu/setup/start/21_locations.txt`
- `game/main_menu/localization/english/actions_l_english.yml`
- `game/dlc/D000_shared/D000_shared.dlc.json`

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

Use these before closing substantial work:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
```

For focused domain work, run the relevant test module first.

## Working Style

- prefer small, test-backed additions
- test against real EU5 files whenever a new domain is introduced
- preserve formatting-sensitive behavior in generic parsers
- fix root causes instead of layering ad hoc special cases
- update docs when the roadmap, environment, or project shape materially changes
