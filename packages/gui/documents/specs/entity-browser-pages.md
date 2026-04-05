# Spec: Entity Browser Pages

## Objective

Extend the read-only browser so it can surface covered entity lists and entity details directly from the stable `eu5miner.inspection` entity-browsing seam.

## In Scope

- entity-system selection in the existing lightweight shell and CLI flow
- list pages for the covered inspection entity systems
- detail pages for a selected entity name within one covered system
- generic rendering of summary, field, and reference dataclasses from core APIs
- synthetic-fixture tests that stay independent from a real EU5 install

## Out Of Scope

- parser, VFS, or domain-model logic in this repo
- editable entity workflows
- bespoke GUI widgets or a replacement for the current `BrowserModel`

## Acceptance Criteria

- the shell can render an entity list page for each covered inspection entity system
- the shell can render a detail page for one selected entity without GUI-local domain parsing
- `--all-systems` remains a thin overview flow and adds entity list pages for covered systems
- the repo remains buildable and testable without a local game install