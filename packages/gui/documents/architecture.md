# EU5MinerGUI Architecture

## Role

This repo owns the desktop application surface for browsing EU5 data through the core `eu5miner` library.

It should not become a second parser, a second domain-model implementation, or a second source-discovery stack.

## Boundaries

- `eu5miner`: parsing, install discovery semantics, VFS behavior, typed domain adapters, inspection catalogs, inspection-backed reports and entity browsing, and mod-planning workflows
- `eu5miner_gui`: presentation, app flow, source/session orchestration, navigation state, GUI-facing page adapters, and widget composition

## Current Stable Seams

The checked-in preview surface is a read-only text browser over stable core seams.

The desktop app should continue to derive its coverage and most of its data from:

- `eu5miner.GameInstall.discover(...)` for auto-discovery and explicit install-root validation
- `eu5miner.inspection.inspect_install(..., mod_roots=...)` and `summarize_install(..., mod_roots=...)` for install and source summaries
- `eu5miner.inspection.list_supported_systems()` and `list_entity_systems()` for ordered sidebar coverage
- `eu5miner.inspection.get_system_report()` for report pages
- `eu5miner.inspection.list_system_entities(..., mod_roots=...)` and `get_system_entity(..., mod_roots=...)` for entity browsing
- thin grouped-package helper wrappers already in `eu5miner_gui` for diplomacy and religion helper pages

## Active Product Direction

The next product slice is the first real Kivy desktop shell.

That slice keeps the app read-only, uses a sidebar plus main detail pane, supports install auto-discovery plus manual override plus extra mod folders, covers all current report and entity seams, keeps current helper-page scope, and preserves a structure that can later support editing.

The current text shell remains valuable as a contract and regression seam, but it is no longer the intended primary user experience once the Kivy desktop shell lands.

## Desktop Layering

The current Kivy desktop slice follows this layering:

1. Core data seams in `eu5miner`
2. Shared GUI adapters that convert core dataclasses and helper views into structured GUI-facing page models
3. Desktop session and navigation state that tracks source selection, active page targets, cached page payloads, and reload generation
4. Kivy widgets that render those page models without containing parser or domain logic

The checked-in desktop package now reflects that split directly:

- `desktop/controller.py`: install/session orchestration, navigation, caching, mod-folder handling, and page loading
- `desktop/navigation.py`: typed navigation targets plus sidebar grouping
- `desktop/adapters.py`: structured page and entity view models over core inspection/helper dataclasses
- `desktop/widgets/`: source strip, sidebar, page host, overview/report/helper rendering, entity browser rendering, and lightweight visual widgets
- `desktop/bootstrap.py`: real Kivy app bootstrap and default desktop launch seam

This keeps widget code thin and makes later editing work a follow-on of state and adapter expansion rather than a rewrite of presentation logic.

## State Model Principles

The desktop shell should keep these concerns separate:

- source state: discovered root, manual install-root override, extra mod folders, reload status, and source-summary metadata
- navigation state: selected page target and deterministic cross-link targets
- page cache state: overview, report, entity-list, entity-detail, and helper payloads for the current source generation
- UI state: sidebar expansion, search text, sort mode, selected entity row, and other purely presentational controls

State transitions should be explicit and testable. Widgets should react to state updates rather than owning the data-loading rules themselves.

## Read-Only Now, Editing Later

The first desktop release remains read-only. It should not implement save, apply, or write-planning behavior.

To keep later editing practical, avoid reducing everything to preformatted multiline text. The GUI should prefer structured page adapters, typed navigation targets, and page-specific view models that can later carry editable fields and dirty-state information without replacing the whole browse architecture.
