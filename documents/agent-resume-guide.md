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
- `src/eu5miner/domains/mod_metadata.py`
- `src/eu5miner/domains/mod_project.py`
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
- Generated helper docs such as `script_docs` and `dump_data_types` are useful if present but cannot be required; prefer local debug-mode dumps when available because they are version-matched to the install, and use the public `modding-digests` mirror as a fallback reference.
- `replace_path` is now normalized into phase-aware VFS rules so merged file views can hide lower-priority files inside replaced subtrees, exact-file write planning can detect higher-priority file or replace-path blockers, subtree planning can report whether a mod would need its own `replace_path` to take clean ownership of a directory tree, the current action layer can classify visible subtree entries as keep, override, or blocked, the emission layer can include intended new file paths so a caller can distinguish create, override, and blocked outcomes for proposed outputs, a mod-oriented emission wrapper can bundle file actions with metadata updates such as adding `replace_path` entries to `.metadata/metadata.json`, the first mod skeleton planner can derive required directories and file paths from those emission plans, targeted emission helpers can now render deterministic metadata.json and content-file write payloads, filesystem materialization helpers can now create the planned directories and write those exact payloads with controlled overwrite behavior, a public `eu5miner.mods` facade now wraps plan, apply, and report operations into one stable workflow surface, and the CLI now exposes matching plan/apply commands with note/warning/error diagnostics plus file-root import helpers for temp-path mod workflows.
- A GUI is planned for convenient data inspection and mod editing; it should sit on top of the same mature library and CLI-facing APIs rather than introducing a separate logic path. The initial phase is read-only browsing; a later phase adds mod data editing capabilities.

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
- localization bundle indexing and cross-reference helpers for customizable, effect, and trigger localization keys
- GUI parsing adapter for top-level constants, templates, grouped `types` libraries, and standalone root definitions such as `window = { ... }` and `basic_priority_dialog = { ... }`
- frontend content helpers for main-menu scenarios plus phase-aware localization discovery and bundle assembly for `loading_screen` and `main_menu`
- default.map adapter covering referenced file paths, scalar settings like `equator_y` and `wrap_x`, sound-toll mappings, and large named-location blocks such as volcanoes, earthquakes, sea zones, lakes, impassable mountains, and non-ownable corridors
- typed CSV helpers for `adjacencies.csv` and `ports.csv`, including integer coordinate parsing and normalization of the trailing marker column in ports rows
- location/setup cross-linking helpers that merge `definitions.txt`, `10_countries.txt`, and `21_locations.txt` into a per-location index with hierarchy paths, country ownership/control categories, capital references, and optional location setup bodies
- typed metadata helpers that normalize shared DLC and local mod `.metadata/metadata.json` content, including optional relationship entries and replace-path/tag accessors
- scripted value adapter for top-level named scalar constants and object formulas, with helper accessors for scalar text versus formula bodies and macro-parameter discovery for formula-based values
- culture adapter for top-level culture definitions with normalized language/color/tags/culture-groups fields, noun/adjective key lists, use-patronym flags, and typed culture-opinion mappings
- religion adapter for top-level religion definitions with normalized group/color/language/enable fields, typed boolean feature flags, modifier bodies, list-like tags and factions, and typed religion-opinion mappings
- country-description-category adapter for empty category definitions plus a setup-country usage index that resolves each country tag's `description_category` to a defined or missing category and groups countries by category name
- scripted-modifier adapter for top-level named modifier definitions with normalized `modifier`, `opinion_modifier`, and `compare_modifier` blocks plus macro-parameter discovery, anchored against the example snippet embedded in the shipped `scripted_modifiers.info`
- scripted-list adapter for top-level named list definitions with normalized `base` and `conditions` fields plus macro-parameter discovery
- scripted-relation adapter for top-level named relation definitions with normalized relation identity fields, common boolean diplomacy flags, typed visibility/effect/evaluation blocks, and stable script-value-like scalar fields for costs, spreads, and trade flows
- on_action adapter for top-level named hook definitions with normalized `trigger`, `effect`, chained `on_actions`, plain `events`, weighted `random_events`, macro-parameter discovery, a parser for the generated `docs/on_actions.log` dump, and a catalog helper that cross-links shipped definitions with documented expected scopes
- building-category adapter for top-level named empty category objects in `common/building_categories`
- building-type adapter for top-level named building definitions with normalized category/pop/build-time/employment fields, common boolean flags, location-rank flags, trigger and modifier blocks, list-like production-method/custom-tag fields, and preserved semantic bodies for the larger long tail of building attributes
- goods adapter for top-level goods definitions with normalized market/category/method fields, common boolean world-origin flags, scalar demand and wealth-threshold sub-blocks, and list-like custom tags
- price adapter for top-level price definitions with normalized core numeric resource-cost fields plus preserved semantic bodies for rarer price keys
- goods-demand-category adapter for top-level demand category definitions with normalized display mode
- goods-demand adapter for top-level demand definitions covering both simple scalar recipes and scripted per-good demand blocks such as `pop_demand`
- production-method adapter for top-level named input/output recipes with normalized goods inputs, `produced`, `output`, `category`, `no_upkeep`, and optional `potential` and `allow` trigger blocks
- employment-system adapter for top-level named definitions with normalized `country_modifier`, `priority`, and `ai_will_do` script blocks
- generic-action adapter for top-level named action definitions with normalized action metadata, repeated `select_trigger` stages, typed selection columns, and preserved script bodies for the long tail of action-specific fields, first validated against `common/generic_actions/markets.txt` and `employment_system.txt`
- VFS replace-path support that loads metadata-driven rules from DLC or mod metadata, hides lower-priority files inside replaced trees, exposes precedence-aware write planning for exact target paths, subtree-level ownership summaries, intended emitted files, and mod-scoped metadata updates, derives concrete recommendations such as create, keep, override, blocked, and add-replace-path, supports a first mod skeleton planner that turns a mod emission plan into required directories, metadata.json handling, intended content files, and separated blocked outputs, includes targeted emission helpers that render metadata.json content and per-file write payloads for intended non-blocked outputs, includes filesystem materialization helpers that apply those explicit planned writes to disk, exposes a public `eu5miner.mods` facade with stable plan/apply/report entrypoints, and now includes CLI plan/apply commands that exercise the same workflow with explicit advisories, warnings, overwrite handling, and recursive content-root inputs

Recently validated:

- setup-country color fields may be scalar values such as `map_FRA` or object-like prefixed blocks such as `rgb { ... }` and `hsv360 { ... }`
- parser-sensitive tests now run with timeouts so performance regressions fail quickly
- localization `.yml` parsing now strips a leading UTF-8 BOM before reading the language header, which matches shipped English bundle files
- shipped GUI files include stable top-level shapes for constants like `@illustration_wide`, templates like `template advances_button_icon`, grouped type libraries like `types EventWindows`, and standalone root objects such as `window = { ... }`
- main-menu scenario files are simple top-level keyed objects with stable fields such as `country`, optional `flag`, `player_playstyle`, and `player_proficiency`; phase-localization content for `loading_screen` and `main_menu` is recursive beneath `localization/<language>` and can be indexed directly
- `default.map` has a small stable top-level contract for referenced file names plus scalar map settings, while its large gameplay-relevant blocks are mostly list-like named-location sets that can be normalized without adding map-specific logic to the generic parser layers
- `adjacencies.csv` currently uses a stable `From/To/Type/Through/start_x/start_y/stop_x/stop_y/Comment` schema with all observed rows typed as `sea`, while `ports.csv` uses `LandProvince/SeaZone/x/y` plus a trailing constant marker column that is better normalized in a typed helper than exposed directly from the generic CSV reader
- `10_countries.txt` is the primary source for country-to-location ownership/control sets and capital locations, while `21_locations.txt` carries location-scoped setup objects and `definitions.txt` supplies the hierarchy path for each location name
- BOM-prefixed Clausewitz script files now parse consistently through the CST and semantic layers, which matters for shipped scalar-heavy files such as `common/script_values/eu4_conversions.txt`
- shipped culture files are flat sets of top-level culture objects with stable list-like blocks such as `tags`, `culture_groups`, `noun_keys`, `adjective_keys`, and `opinions`, while shipped religion files are flat top-level religion objects with scalar identity fields plus list-like `tags`, `custom_tags`, `unique_names`, `factions`, and `opinions`
- shipped `common/country_description_categories/categories.txt` is intentionally minimal, but it pairs directly with `setup/countries/*.txt` through each country's `description_category` field, so the useful abstraction is a cross-linked usage view rather than just a raw parser
- this install currently ships only `common/scripted_modifiers/scripted_modifiers.info` for scripted modifiers, but that info file includes a parseable example block that is sufficient to anchor the first typed adapter without needing an external dump yet
- shipped `common/scripted_lists/*.txt` files are straightforward top-level keyed objects with `base` and `conditions`, while `common/scripted_relations/*.txt` files are large but structurally stable top-level relation objects with a reusable mix of scalar flags, cost/script-value fields, and trigger/effect/evaluation blocks; unlike scripted modifiers, relations have plenty of real shipped files to validate against directly
- shipped `common/on_action/*.txt` files are flat top-level hook definitions with a stable mix of `trigger`, `effect`, chained `on_actions`, plain `events`, and weighted `random_events`; the locally generated dump at `OneDrive/Documents/Paradox Interactive/Europa Universalis V/docs/on_actions.log` provides a reliable optional source for expected-scope metadata and confirms which hooks are code-defined versus fully scripted
- shipped `common/building_categories/00_default.txt` is a minimal list of named empty category objects, while shipped `common/building_types/*.txt` files are flat top-level building definitions with a large but stable core of scalar fields and script blocks; the readme in `common/building_types/readme.txt` is enough to anchor the first typed adapter, and the `dump_data_types` output only confirms generic engine types like `Building` and `BuildingType` rather than exposing parser-critical field schema
- shipped `common/goods/*.txt` and `common/prices/*.txt` have straightforward top-level keyed object models anchored well by their readmes, while `common/goods_demand_category/00_default.txt` is minimal and `common/goods_demand/*.txt` uses two stable shapes: simple scalar demand recipes and scripted per-good blocks under definitions like `pop_demand`; this still does not justify a required `dump_data_types` dependency, because the dump confirms engine type names but not the field-level syntax that the shipped files already expose directly
- shipped `common/production_methods/unsorted_building_inputs.txt` is a straightforward top-level recipe family matching its readme, and `common/employment_systems/00_default.txt` is a small top-level named-object family with three stable script blocks; neither family currently needs dump-backed schema help to parse cleanly
- shipped `common/generic_actions/readme.txt` defines a reusable top-level action contract, while `common/generic_actions/markets.txt` and `employment_system.txt` confirm a stable mix of scalar metadata, repeated `select_trigger` blocks, typed `column` definitions, and effect/AI script bodies that justify a generic adapter rather than a market-only parser

## Next Planned Work

The economy and production layer now includes both market primitives, core production rules, and the first generic market action helpers. The next recommended domain target is `additional market-adjacent helpers such as attribute columns`, followed by the rest of the economy and production systems.

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
