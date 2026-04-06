# Spec: First Real Kivy Desktop Shell

This spec replaces the previous implied PySide direction with one concrete implementation plan for the first real EU5MinerGUI desktop application. The slice stays read-only, uses Kivy as the desktop UI framework, preserves the current inspection-backed and helper-page coverage, and keeps parsing and domain logic in the core `eu5miner` library.

## Inputs And Fixed Decisions

The following decisions are fixed for this slice:

- ship an actual GUI, not a second CLI-first browsing workflow
- keep the first desktop release read-only
- use a sidebar plus main detail pane layout
- support install auto-discovery, manual install-root override, and additional mod folders in one session
- keep full current systems coverage across supported reports, browseable entity systems, and shipped helper pages
- make entity lists efficiently searchable and filterable for large datasets
- support clickable cross-links where the target page is deterministic
- add some visualizations where they clearly improve comprehension, but avoid speculative canvases
- keep the architecture practical for later editing
- keep parser, VFS, and domain-model logic in core `eu5miner`

## Scope

Ship in this slice:

- one Kivy desktop window with a source strip, sidebar navigation, and main detail pane
- overview, supported-system report, browseable-entity, entity-detail, diplomacy-helper, and religion-helper pages
- install auto-discovery, manual install-root override, extra mod-folder selection, and reload
- efficient entity-list search, filtering, sorting, and selection-driven detail loading
- deterministic clickable navigation between pages and between resolvable entity references
- a small set of high-signal visualizations for overview and helper pages
- a state and adapter architecture that keeps later editing feasible without implementing editing now

Do not ship in this slice:

- editing or write-back workflows
- a raw file browser or text editor
- a second long-lived text-shell UX as the main product surface
- global full-text indexing across every loaded page
- a generic graph explorer, zoomable map canvas, or other framework-heavy visualization work
- GUI-local parser, VFS, or domain-model logic

## Architectural Context And Reuse Plan

The current repo already has the correct domain boundary. The checked-in shell builds a `BrowserModel` over core inspection catalogs, report pages, entity pages, and thin helper wrappers. The Kivy slice should reuse that boundary and replace the presentation layer, not create a second data model in widget code.

Use the following existing seams as the source of truth:

- `eu5miner.GameInstall.discover(root | None)` for auto-discovery and explicit install-root validation
- `eu5miner.inspection.inspect_install(..., mod_roots=...)` and `summarize_install(..., mod_roots=...)` for source summaries and merged-source visibility with extra mod folders
- `eu5miner.inspection.list_supported_systems()` and `list_entity_systems()` for sidebar groups, order, and descriptions
- `eu5miner.inspection.get_system_report()` for report pages
- `eu5miner.inspection.list_system_entities(..., mod_roots=...)` and `get_system_entity(..., mod_roots=...)` for entity browsing
- current helper wrappers in `src/eu5miner_gui/diplomacy_helpers.py` and `src/eu5miner_gui/religion_helpers.py` for the shipped helper scope
- the current `browser.py` page-key grammar and page categories as the compatibility baseline during the desktop transition

Do not duplicate supported-system catalogs, entity-system catalogs, install merging, or entity parsing in the Kivy layer.

## Recommended Module Plan

Keep the existing text shell intact while adding a dedicated desktop package.

Recommended additions:

- `src/eu5miner_gui/desktop/__init__.py`
- `src/eu5miner_gui/desktop/bootstrap.py`
- `src/eu5miner_gui/desktop/state.py`
- `src/eu5miner_gui/desktop/navigation.py`
- `src/eu5miner_gui/desktop/controller.py`
- `src/eu5miner_gui/desktop/adapters.py`
- `src/eu5miner_gui/desktop/widgets/source_bar.py`
- `src/eu5miner_gui/desktop/widgets/sidebar.py`
- `src/eu5miner_gui/desktop/widgets/page_host.py`
- `src/eu5miner_gui/desktop/widgets/overview_page.py`
- `src/eu5miner_gui/desktop/widgets/report_page.py`
- `src/eu5miner_gui/desktop/widgets/entity_browser_page.py`
- `src/eu5miner_gui/desktop/widgets/helper_page.py`
- `src/eu5miner_gui/desktop/widgets/visuals.py`

Existing modules that should remain relevant:

- `src/eu5miner_gui/app.py` and `src/eu5miner_gui/cli.py` as the launch seam, with the desktop app becoming the default behavior
- `src/eu5miner_gui/browser.py` as the current shared navigation and regression contract until any structured adapter split is complete
- `src/eu5miner_gui/diplomacy_helpers.py` and `src/eu5miner_gui/religion_helpers.py` as the thin helper integration layer

## Window And Widget Contract

### Root Window

The desktop app should open one main window.

Required layout:

- top source strip for source controls and current-source status
- left sidebar for navigation
- right main detail pane for the active page

The overall app contract remains sidebar plus main detail pane even if individual page widgets use internal split panes.

### Source Strip

Required controls:

- discovered-or-selected install root display
- manual install-root chooser
- add mod-folder action
- remove mod-folder action for selected extra mod folder
- reload action
- compact status text for discovery and load errors

Required behavior:

- the app attempts `GameInstall.discover()` on startup with no explicit root
- a successful auto-discovery immediately loads the overview page
- a failed auto-discovery leaves the app on a recoverable empty-state overview instead of aborting startup
- a manual install-root choice is validated through `GameInstall.discover(explicit_root)` before becoming active session state
- extra mod folders are tracked in insertion order, normalized, and deduplicated for the current session

### Sidebar

The sidebar should be built from the existing core and helper catalogs, not GUI-local copies.

Required groups:

- `Overview`
- `Systems`
- `Entities`
- `Helpers`

Required entries:

- one `Overview` item
- one item for every `list_supported_systems()` entry, in core order
- one item for every `list_entity_systems()` entry, in core order
- explicit helper items for `war-flow`, `diplomacy-graph`, and `religion-overview`

The sidebar should stay stable even when the current source cannot load every page. Unavailable pages remain selectable and explain why they are unavailable.

### Main Detail Pane

The detail pane must support these page types:

- install overview
- system report
- entity browser page for one browseable system
- direct entity detail target
- diplomacy helper page
- religion helper page

The first desktop release does not need tabs, multiple windows, or detachable panes.

## State Model

Keep state explicit and separate from widgets.

### Top-Level App State

Recommended top-level structure:

- `SourceSessionState`
- `NavigationState`
- `PageCacheState`
- `UiState`

### SourceSessionState

Required fields:

- discovered install root, if any
- manual install-root override, if any
- active install root
- extra mod folders
- current source summary or empty-state reason
- reload generation token
- load status: idle, loading, ready, or error

### NavigationState

Represent navigation as structured targets, not only strings.

Required target kinds:

- `overview`
- `report(system)`
- `entity_list(system)`
- `entity_detail(system, name)`
- `helper(name)`

Page keys should remain available as compatibility identifiers, but widgets and controllers should work from structured navigation values.

### PageCacheState

Cache page payloads per source generation.

Minimum cache entries:

- overview payload
- report payloads by system
- entity summary lists by system
- entity detail payloads by `(system, entity_name)`
- helper payloads by helper name

Cache invalidation rule:

- any install-root change or mod-folder change increments the generation and invalidates all cached payloads for the prior generation

### UiState

UI-only state should stay out of the source and navigation models.

Examples:

- sidebar expansion
- active entity-list search text
- current entity-list sort mode
- current entity-list filter mode
- selected entity row in the current entity page
- helper-section collapse or expansion state if implemented

## Data Flow

Recommended data flow:

1. App boot attempts install auto-discovery.
2. Controller updates `SourceSessionState` with either the discovered install or a recoverable empty state.
3. Sidebar selection updates `NavigationState`.
4. Controller loads or reuses the payload for the selected target using core inspection or helper seams plus current `mod_roots` where supported.
5. Adapter layer converts the payload into Kivy-facing page view models.
6. Widgets render the view model and emit structured navigation or source-change events back to the controller.

Do not let widgets call inspection or helper functions directly.

## Entity-List Search And Filter Strategy

Large entity lists are one of the main reasons for the desktop slice, so the GUI must not reuse the text shell's paging model as the main interaction pattern.

Required strategy:

- load one system's `EntitySummary` rows per entity page activation or reload cycle
- build one cached search record per entity summary with normalized searchable text assembled from name, group, description, and source-facing metadata when present
- keep entity summaries in memory for the active system and filter against those cached normalized records instead of reloading from core on each search change
- use Kivy view virtualization for the visible list instead of building one widget per entity row
- load full entity detail only for the selected row, not for every row up front
- debounce search input before recomputing the visible set

Recommended first-release behavior:

- search is case-insensitive substring matching
- sorting supports the existing shell semantics: `name`, `group`, and `source`
- filter controls may start with one free-text box and one sort selector; do not add advanced query syntax yet
- visible result count and active filter should remain obvious in the UI

Recommended Kivy implementation:

- `RecycleView` for the entity list surface
- lightweight row data objects rather than widget-local inspection objects
- a controller-managed filtered index list so sorting and filtering operate on cached summaries, not on row widgets
- selection-driven detail fetch and detail-pane update

Global cross-system search and background indexing are out of scope for this slice.

## Cross-Link Contract

Use explicit navigation targets, not text scraping, for clickable links.

Required clickable links:

- sidebar item to page navigation
- entity row to entity detail navigation
- entity-detail references when core already exposes a resolvable target system and target name
- report-page links where the target is deterministic, such as report to its browseable entity list when applicable

Allowed fallback behavior:

- render unresolved references as plain text with a non-clickable visual treatment
- do not invent heuristic links for helper sections that only expose free-form names

## Visualizations

Add only visualizations that clearly improve comprehension over plain text.

Ship in this slice:

- overview source summary visualization: a compact source-layer strip or stack that makes game, DLC, and extra mod precedence easier to scan than raw lines alone
- helper summary visualization: compact bars or chips for relationship counts in diplomacy and religion helper pages

Do not ship in this slice:

- a generic node-and-edge graph viewer
- panning map views
- highly interactive canvases that dominate the browsing workflow

## Mod Folder Handling

The desktop shell must support extra mod folders as a first-class source selection input.

Required behavior:

- extra mod folders are session-local and user-managed from the source strip
- overview, install summary, system reports, entity lists, and entity details should pass `mod_roots` through the existing `eu5miner.inspection` seam
- source-summary UI should show which extra mod folders are active in the current session
- reloading after a mod-folder change should invalidate cached page payloads and rebuild the current page over the new merged source set

Current helper-page limitation to preserve explicitly:

- the checked-in diplomacy and religion helper wrappers currently build from representative install files on `GameInstall` and do not yet have a `mod_roots`-aware loading seam

Implementation rule:

- keep the Kivy slice thin over the current helper wrappers for the initial desktop delivery, and surface helper source scope honestly in the UI
- if mod-aware helper pages become required during implementation, resolve that as a narrow core-library follow-up instead of copying representative-file resolution into the GUI repo

## Read-Only Architecture That Can Later Support Editing

This slice remains read-only, but its structure should make later editing additive rather than disruptive.

Architectural rules:

- keep source/session state separate from widget state
- keep navigation targets typed and explicit
- prefer structured page adapters over pre-rendered multiline text
- keep one controller or orchestration layer between widgets and core APIs
- keep the current text shell available as a regression seam while the desktop app lands

Practical implication:

- if `browser.py` is too text-renderer-centric for direct GUI reuse, split shared page-building and navigation structures into reusable adapter types that both the text renderer and Kivy widgets can consume

Do not add dirty-state tracking, write-planning actions, or edit commands in this slice.

## Testing Approach

Default validation must remain independent from a local EU5 install.

Required coverage:

- headless desktop bootstrap tests
- source-state tests for discovery success, discovery failure, manual override, mod-folder add or remove, and reload
- sidebar coverage tests that prove ordering comes from the core inspection catalogs plus the explicit helper list
- entity-browser tests for search, sort, filter count, selection, and lazy detail loading
- cross-link tests for resolvable entity references and report-to-list navigation
- helper-page tests for both existing diplomacy helper pages and the existing religion helper page
- continued shell-level contract coverage for the current browser model and page-key grammar

Recommended test modules:

- `tests/test_gui_shell.py` remains the browser and compatibility seam
- `tests/test_desktop_bootstrap.py`
- `tests/test_desktop_navigation.py`
- `tests/test_desktop_entities.py`
- `tests/test_desktop_sources.py`

Use synthetic installs and patched inspection or helper seams rather than requiring a real EU5 install. Configure Kivy tests to run with a headless or mock window provider appropriate for CI.

## Acceptance Criteria

- `eu5miner-gui` launches a Kivy desktop window by default instead of printing the text browser by default
- startup attempts install auto-discovery and lands in either a loaded overview state or a recoverable empty-state overview
- users can choose a manual install root, add extra mod folders, remove extra mod folders, and reload without restarting the app
- the sidebar exposes all current supported system reports, all current browseable entity systems, and the shipped diplomacy and religion helper pages in the intended order
- selecting a supported system renders the corresponding report page from core APIs without GUI-local parsing
- selecting a browseable entity system renders a searchable and sortable entity list plus a detail panel for the current selection
- selecting diplomacy and religion helper entries renders the existing helper-page content over the current thin grouped-package helper seams
- clickable navigation works for sidebar transitions, entity-row selection, and resolvable entity references
- overview and helper pages include the limited high-signal visualizations defined above
- the UI exposes no edit, save, apply, or write-planning actions
- default tests remain runnable without a local EU5 install

## Phased Delivery Inside This Slice

The slice should still ship as one coherent Kivy desktop shell, but implementation can proceed in this order:

### Phase 1: Desktop Skeleton And Source State

- add the Kivy dependency and desktop bootstrap
- add headless-testable app startup
- implement source strip, auto-discovery, manual root selection, extra mod-folder management, reload, and overview page
- make the desktop window the default launch path

### Phase 2: Sidebar And Read-Only Pages

- implement sidebar groups and deterministic navigation targets
- render overview, system report, and existing helper pages in the main detail pane
- add overview and helper visual summaries

### Phase 3: Large Entity Browsing

- implement the entity browser page with virtualized rows, debounced search, sort, filter state, and selection-driven detail loading
- add entity-detail cross-links and report-to-list links where deterministic
- finish unavailable-page handling and read-only polish

Keep these phases under one active spec and one release target. Do not split them into a separate CLI modernization track.

## Validation

- `uv run pytest`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

Use the repository's centralized environment and a headless Kivy test configuration suitable for hosted CI.

## Open Questions

No blocking product questions remain for this slice.

One implementation dependency is explicit: if helper pages must reflect extra mod-folder overlays rather than install-only representative files, add that capability as a narrow `eu5miner` seam instead of solving it with GUI-local file resolution.