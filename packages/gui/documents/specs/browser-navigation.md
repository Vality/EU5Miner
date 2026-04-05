# Spec: Browser Navigation

## Objective

Refine the existing read-only browser so the preview shell has real page navigation instead of a single full-session dump.

## In Scope

- explicit page-key focus over already-supported overview, report, entity-list, and entity-detail pages
- page index mode for listing the current browser session without rendering page bodies
- lightweight case-insensitive filtering over loaded pages using page metadata and rendered section lines
- shell and CLI wiring that stay thin over `eu5miner.inspection` and existing `BrowserModel` pages
- synthetic-fixture tests that remain independent from a real EU5 install

## Out Of Scope

- heavyweight GUI frameworks or widget hierarchies
- new parser, VFS, or domain-model behavior in this repo
- install-required tests in the default validation path
- fuzzy search, pagination, or richer entity-graph traversal beyond loaded pages

## Acceptance Criteria

- the shell shows a page index and renders only the selected page by default
- the CLI can focus a page directly with keys such as `report:map` or `entity:map:stockholm`
- the CLI can list pages without page bodies and can filter the current loaded page set without requiring a real install in tests