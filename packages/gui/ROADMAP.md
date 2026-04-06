# EU5MinerGUI Roadmap

This roadmap is intentionally short. The GUI repo should stay focused on UI and product-surface work, not on reimplementing library logic.

## Current Baseline

The current preview baseline now includes:

- repo and package alignment with the core library workflow
- a launchable CLI and app shell
- a structured read-only browser model with an overview page and per-system report pages
- browsing for one selected system or all supported systems from a chosen install
- explicit page-key focus, page index mode, lightweight filtering, and concrete reopen hints when filters hide the current session selection
- page-index windowing, section truncation, and navigation hints for larger browser sessions
- entity-list sorting, dedicated entity windowing, detail mode, and concrete list-to-detail jump hints
- graceful unavailable-page handling for partial or synthetic installs, including overview recovery guidance and stable session-position context

That means the next work should keep the shipped browser aligned with the core preview contract rather than reopening another baseline browse-flow slice.

## Next Recommended Order

### 1. Preview Alignment With The Core Library

Goal: keep the GUI thin over the intended stable seams as the preview line evolves.

Execution spec: `documents/specs/preview-alignment.md`

Use this slice for:

- docs and examples that match the shipped inspection-backed browser behavior
- focused test updates when the core inspection facade changes or tightens its stable catalog contract
- local source alignment and contract-locking around supported-system and browseable-entity-system coverage
- dependency and release alignment with the core preview contract

Do not reopen landed browse-refinement slices unless a core contract change forces a narrow follow-up.

### 2. Defer Editing Workflows

Goal: keep write or editor-oriented work out of scope until a concrete cross-repo plan exists.

Editing is not the current next release slice for this repo.

## Rules

- parsing work stays in `eu5miner`
- UI work stays here
- the current read-only browser model is the baseline, not a prototype to replace by default
- major follow-on slices should be backed by a spec in `documents/specs/`
