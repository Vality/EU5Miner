# Spec: Large Entity-List Browsing

## Objective

Refine the lightweight read-only browser so large covered entity lists remain practical to scan and jump through without moving data logic out of the stable `eu5miner.inspection` facade.

## In Scope

- explicit entity-list sorting controls over already-loaded `EntitySummary` rows
- entity-list-specific limit and offset controls that page large lists without affecting unrelated page sections
- compact and detail list modes for the same entity list page
- clearer list-to-detail jump hints that expose concrete entity detail page keys from the visible entity window
- synthetic-fixture tests that remain independent from a real EU5 install

## Out Of Scope

- parser, VFS, or domain-model behavior in this repo
- interactive widgets, incremental loading, or a heavy GUI framework
- core-library pagination or query APIs
- install-required tests in the default validation path

## Acceptance Criteria

- entity list pages sort by a predictable explicit mode and can preserve source order when requested
- large entity lists can be browsed with dedicated entity-window controls instead of only generic section truncation
- users can switch between compact summaries and detail rows without leaving the current lightweight shell model
- list pages expose enough detail-page hints to jump from a visible entity row into a specific entity detail page