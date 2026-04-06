# EU5MinerGUI Roadmap

This roadmap is intentionally short. The GUI repo should stay focused on UI and product-surface work, not on reimplementing library logic.

## Current Baseline

The current preview baseline now includes:

- repo and package alignment with the core library workflow
- a launchable CLI and app shell
- a structured read-only browser model with an overview page and per-system report pages
- browsing for one selected system or all supported systems from a chosen install
- thin diplomacy helper pages over grouped `eu5miner.domains.diplomacy` war-flow and diplomacy-graph seams using representative install files
- one thin religion helper page over grouped `eu5miner.domains.religion` catalog/report seams using representative install files
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

### 2. Diplomacy Helper Pages Over Stable Grouped Packages

Goal: keep the first grouped-package expansion explicit and narrow by surfacing diplomacy helper pages over the stable core diplomacy helper surface.

Execution spec: `documents/specs/diplomacy-helper-pages.md`

Use this slice for:

- one explicit helper-page family in the existing browser model and CLI flow
- representative install loading through `GameInstall.representative_files()`
- thin `war-flow` and `diplomacy-graph` page rendering over grouped `eu5miner.domains.diplomacy` parsers and helper builders
- focused contract tests that lock helper names, page keys, page titles, and representative summary sections

The first checked step-2 slice in this category is now explicit and should stay the reference pattern for any future helper-page work.

The second checked follow-on in this category is also now explicit and deliberately small: one representative-file-backed religion helper page over the grouped `eu5miner.domains.religion` surface.

Execution spec: `documents/specs/religion-helper-pages.md`

Boundary preserved by that shipped follow-on:

- add exactly one new opt-in helper page: `helper:religion-overview`
- expose that same page through one explicit selector, `--religion-helper religion-overview`, plus the alias `religion-helper:religion-overview`
- load only the fixed representative religion file set already curated by `GameInstall.representative_files()`
- build the page only from grouped `eu5miner.domains.religion` parser and report exports
- keep the page outside `--all-systems` and outside the generic inspection entity browser

Do not use this slice to widen `--all-systems`, invent religion parsing in the GUI repo, or bypass the current browser/page model with bespoke helper-only workflows.

### 3. Defer Editing Workflows

Goal: keep write or editor-oriented work out of scope until a concrete cross-repo plan exists.

Editing is not the current next release slice for this repo.

## Rules

- parsing work stays in `eu5miner`
- UI work stays here
- the current read-only browser model is the baseline, not a prototype to replace by default
- major follow-on slices should be backed by a spec in `documents/specs/`
