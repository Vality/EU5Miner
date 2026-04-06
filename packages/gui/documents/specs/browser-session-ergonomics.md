# Spec: Browser Session Ergonomics

## Objective

Refine the lightweight read-only shell so larger browser sessions stay readable without moving data logic out of the core `eu5miner.inspection` facade.

## In Scope

- page-index windowing with explicit limit and offset controls
- section-level truncation controls for long rendered lists such as entity collections
- lightweight navigation hints that expose the current page key and nearby parent or related pages
- clearer empty-filter feedback that explains filtering only applies to already-loaded pages
- synthetic-fixture tests that remain independent from a real EU5 install

## Out Of Scope

- parser, VFS, or domain-model behavior in this repo
- interactive TUI widgets or keyboard navigation
- core-library pagination APIs or GUI-local entity caching
- install-required tests in the default validation path

## Acceptance Criteria

- large page indexes can be narrowed with explicit window controls from the CLI
- long rendered sections can be truncated intentionally while keeping the full output available on demand
- entity list and detail pages include enough navigation hints to move between overview, list, and detail views from the shell
- empty page-filter results explain why nothing matched and how to widen the loaded session