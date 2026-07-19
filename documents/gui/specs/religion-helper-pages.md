# Religion Helper Page Over Stable Grouped Packages

## Status

This spec defines the second checked step-2 GUI breadth slice after the shipped diplomacy helper pages.

## Objective

Add one thin religion helper page to the existing read-only browser by wrapping the stable grouped `eu5miner.domains.religion` helper surface over representative install files. The GUI repo should only route selection, assemble page sections, and render output inside the existing browser model.

## Architectural Context

The current browser baseline is centered on `eu5miner.inspection` report pages, entity pages, and the shipped diplomacy helper pages. This slice is the next deliberate grouped-package expansion because core already exposes a stable religion helper family that is richer than the inspection facade and still narrow enough to wrap directly.

Use only stable core seams intended for downstream consumers:

- `eu5miner.GameInstall`
- grouped exports from `eu5miner.domains.religion`

Do not import core internals from `eu5miner.domains.religion.*`, and do not move religion parsing into the browser, app, or CLI layers.

## Scope

- add one GUI-local religion helper module at `src/eu5miner.gui/religion_helpers.py`
- expose exactly one explicit helper selection through `--religion-helper religion-overview`
- support direct page focus through `helper:religion-overview` and `religion-helper:religion-overview` aliases
- load representative files through `GameInstall.representative_files()`
- build the page from grouped `parse_religion_document`, `parse_religious_aspect_document`, `parse_religious_faction_document`, `parse_religious_focus_document`, `parse_religious_school_document`, `parse_religious_figure_document`, `parse_holy_site_document`, `parse_holy_site_type_document`, `build_religion_catalog`, and `build_religion_report`
- keep helper-page rendering inside the current browser, page, and session-summary shell instead of introducing a second navigation surface
- cover the slice with synthetic-install tests that prove the GUI stays thin over grouped-package helpers

## Target Files

- `src/eu5miner.gui/religion_helpers.py`
- `src/eu5miner.gui/browser.py`
- `src/eu5miner.gui/app.py`
- `src/eu5miner.gui/cli.py`
- `tests/test_gui_shell.py`

## CLI And Browser Contract

- `--religion-helper religion-overview` selects `helper:religion-overview`
- `--page helper:religion-overview` and `--page religion-helper:religion-overview` resolve the same helper page
- overview output continues to list the available religion helper name and description when no install is selected
- the helper page remains explicit opt-in rather than becoming part of `--all-systems`
- the helper page does not replace or widen the existing `entities:religion` inspection-backed entity list flow

## Page Contract

### `helper:religion-overview`

Purpose: render the grouped-package religion helper report for representative religion files.

Representative keys:

- `religion_sample`
- `religion_secondary_sample`
- `religion_muslim_sample`
- `religion_tonal_sample`
- `religion_dharmic_sample`
- `religious_aspect_sample`
- `religious_aspect_secondary_sample`
- `religious_faction_sample`
- `religious_focus_sample`
- `religious_school_sample`
- `religious_school_secondary_sample`
- `religious_figure_sample`
- `religious_figure_secondary_sample`
- `holy_site_type_sample`
- `holy_site_sample`
- `holy_site_secondary_sample`

Rendered sections:

- `Representative files`
- `Coverage summary` with definition counts for religions, religious aspects, religious factions, religious focuses, religious schools, religious figures, holy site types, and holy sites, plus link counts for religion to aspect, faction, focus, school, holy site, and figure relationships
- `Missing references` for religious factions, religious focuses, and religious schools
- `Representative links` for those same six relationship families

## Implementation Notes

- keep religion-specific file selection and report shaping in `religion_helpers.py`
- keep the browser, app, and CLI layers limited to helper enumeration, selection routing, and rendering existing helper sections
- preserve grouped-package vocabulary in page labels instead of inventing GUI-local relationship names
- use `parse_holy_site_type_document` only for fixed representative-file provenance and holy-site-type counts in the summary; do not widen this slice into a second holy-site helper page
- use synthetic installs in tests so the default workflow stays independent of a local EU5 install

## Out Of Scope

- new parser, VFS, or domain-model logic in this repo
- widening `--all-systems` into a generic helper loader
- helper-specific drill-down, secondary religion helper pages, or a generic helper registry
- routing the page through `eu5miner.inspection` instead of the grouped religion package
- editing workflows or install-required validation in the default workflow

## Acceptance Criteria

- the shell can render `helper:religion-overview` from a selected install
- the CLI exposes `--religion-helper` and page aliases without duplicating religion parsing logic in the GUI repo
- the helper page derives its content from grouped `eu5miner.domains.religion` builders over representative install files
- helper name, page keys, page title, representative summary sections, and relationship-category sections are locked by focused synthetic-install tests
- the repo remains buildable and testable without a local EU5 install

## Validation

- `uv run pytest tests/test_gui_shell.py`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

## Sequencing Notes

This is the second explicit checked step-2 breadth slice after the shipped diplomacy helper pages. Keep future follow-ons to one opt-in helper page over a fixed representative file bundle. Do not combine them with a generic helper browser, a helper taxonomy refactor, or multiple helper families in the same slice.