# Diplomacy Helper Pages Over Stable Grouped Packages

## Status

This spec now defines the first explicit step-2 GUI implementation slice and the narrow pattern future helper-page work should preserve.

## Objective

Add one thin diplomacy helper-page family to the existing read-only browser by wrapping the stable grouped `eu5miner.domains.diplomacy` helper surface over representative install files. The GUI repo should only route selection, assemble page sections, and render output inside the existing browser model.

## Architectural Context

The current browser baseline is centered on `eu5miner.inspection` report pages and entity pages. This slice is the first deliberate grouped-package expansion because core already exposes a stable diplomacy helper family that is richer than the inspection facade and still narrow enough to wrap directly.

Use only stable core seams intended for downstream consumers:

- `eu5miner.GameInstall`
- grouped exports from `eu5miner.domains.diplomacy`

Do not import core internals from `eu5miner.domains.diplomacy.*`, and do not move diplomacy parsing into the browser, app, or CLI layers.

## Scope

- add one GUI-local helper-page family in `src/eu5miner_gui/diplomacy_helpers.py`
- expose explicit helper selection through `--diplomacy-helper`
- support direct page focus through `helper:<name>` and `diplomacy-helper:<name>` aliases
- load representative files through `GameInstall.representative_files()`
- build `war-flow` pages from grouped `parse_casus_belli_document`, `parse_wargoal_document`, `parse_peace_treaty_document`, `parse_subject_type_document`, `build_war_flow_catalog`, and `build_war_flow_report`
- build `diplomacy-graph` pages from the same grouped war-flow seams plus grouped `parse_country_interaction_document`, `parse_character_interaction_document`, `build_diplomacy_graph_catalog`, and `build_diplomacy_graph_report`
- keep helper-page rendering inside the current browser/page/session-summary shell instead of introducing a second navigation surface
- cover the slice with synthetic-install tests that prove the GUI stays thin over grouped-package helpers

## Target Files

- `src/eu5miner_gui/diplomacy_helpers.py`
- `src/eu5miner_gui/browser.py`
- `src/eu5miner_gui/app.py`
- `src/eu5miner_gui/cli.py`
- `tests/test_gui_shell.py`

## CLI And Browser Contract

- `--diplomacy-helper war-flow` selects `helper:war-flow`
- `--diplomacy-helper diplomacy-graph` selects `helper:diplomacy-graph`
- `--page helper:war-flow` and `--page diplomacy-helper:war-flow` resolve the same helper page
- overview output continues to list the available diplomacy helper names and descriptions when no install is selected
- helper pages remain explicit opt-in pages rather than becoming part of `--all-systems`

## Page Contracts

### `helper:war-flow`

Purpose: render the grouped-package war-flow helper report for representative diplomacy files.

Representative keys:

- `casus_belli_sample`
- `casus_belli_secondary_sample`
- `casus_belli_subject_sample`
- `casus_belli_religious_sample`
- `casus_belli_trade_sample`
- `wargoal_sample`
- `peace_treaty_sample`
- `peace_treaty_secondary_sample`
- `peace_treaty_special_sample`
- `subject_type_sample`
- `subject_type_secondary_sample`
- `subject_type_colonial_sample`
- `subject_type_hre_sample`
- `subject_type_special_sample`

Rendered sections:

- `Representative files`
- `Coverage summary` with definition counts for casus belli, wargoals, peace treaties, and subject types, plus link counts for casus belli to wargoal, peace treaty to casus belli, and peace treaty to subject type relationships
- `Missing references` for wargoals, casus belli, and subject types
- `Representative links` for the same three relationship families

### `helper:diplomacy-graph`

Purpose: render the grouped-package diplomacy-graph helper report for representative diplomacy and interaction files.

Representative keys:

- all `helper:war-flow` keys
- `country_interaction_sample`
- `country_interaction_secondary_sample`
- `character_interaction_sample`
- `character_interaction_secondary_sample`
- `character_interaction_ui_sample`

Rendered sections:

- `Representative files`
- `Coverage summary` with country-interaction and character-interaction definition counts, plus link counts for peace treaty to casus belli, peace treaty to subject type, country interaction to casus belli, country interaction to subject type, country interaction to country interaction, and character interaction to subject type relationships
- `Missing references` for casus belli, subject types, and country interactions
- `Representative links` for those same relationship families

## Implementation Notes

- keep diplomacy-specific file selection and report shaping in `diplomacy_helpers.py`
- keep the browser, app, and CLI layers limited to helper enumeration, selection routing, and rendering existing helper sections
- preserve grouped-package vocabulary in page labels instead of inventing GUI-local relationship names
- use synthetic installs in tests so the default workflow stays independent of a local EU5 install

## Out Of Scope

- new parser, VFS, or domain-model logic in this repo
- widening `--all-systems` into a generic helper loader
- bespoke GUI widgets, graph navigation, or helper-specific detail drill-downs
- editing workflows or install-required validation in the default workflow
- helper-page families outside diplomacy before core exposes an equally stable grouped-package seam

## Acceptance Criteria

- the shell can render `helper:war-flow` and `helper:diplomacy-graph` from a selected install
- the CLI exposes `--diplomacy-helper` and page aliases without duplicating diplomacy parsing logic in the GUI repo
- helper pages derive their content from grouped `eu5miner.domains.diplomacy` builders over representative install files
- helper names, page keys, page titles, and representative summary sections are locked by focused synthetic-install tests
- the repo remains buildable and testable without a local EU5 install

## Validation

- `uv run pytest tests/test_gui_shell.py`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

## Sequencing Notes

This is the first explicit checked step-2 GUI slice. Future helper-page work should follow the same pattern: one named helper family, explicit page keys, explicit representative-file coverage, and focused tests instead of a generic helper browser abstraction.