# EU5MinerGUI Roadmap

This roadmap is intentionally short. The GUI repo should stay focused on UI and product-surface work, not on reimplementing library logic.

## Current Baseline

The current preview baseline now includes:

- repo and package alignment with the core library workflow
- a launchable CLI and app shell
- a structured read-only browser model with an overview page and per-system report pages
- browsing for one selected system or all supported systems from a chosen install
- graceful unavailable-page handling for partial or synthetic installs

That means the next work should refine the shipped read-only browser, not restart shell or scaffolding work.

## Next Recommended Order

### 1. Read-Only Browsing Refinement

Goal: improve the existing browser model and browse flow.

Use this slice for:

- clearer page selection and session flow
- better presentation of overview, report, and unavailable states
- thin UI-facing structure over the existing `eu5miner.inspection` reports

### 2. Preview Alignment With The Core Library

Goal: keep the GUI thin over the intended stable seams as the preview line evolves.

Use this slice for:

- docs and examples that match the shipped browser behavior
- test updates when the core inspection facade gains or tightens stable behavior
- dependency and release alignment with the core preview contract

### 3. Defer Editing Workflows

Goal: keep write or editor-oriented work out of scope until a concrete cross-repo plan exists.

Editing is not the current next release slice for this repo.

## Rules

- parsing work stays in `eu5miner`
- UI work stays here
- the current read-only browser model is the baseline, not a prototype to replace by default
- major follow-on slices should be backed by a spec in `documents/specs/`
