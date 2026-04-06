# Spec Index

These specs are the execution layer under `ROADMAP.md`.

## Current Status

The two specs in this folder describe the baseline that has already landed for the preview repo.

## Landed Baseline Specs

- `read-only-shell.md`: completed foundation for the launchable app shell and CLI entrypoint
- `read-only-data-browser.md`: completed baseline for the structured overview and per-system report browser model
- `entity-browser-pages.md`: completed browse refinement for covered entity list/detail pages over `eu5miner.inspection`
- `browser-navigation.md`: completed navigation refinement for explicit page focus, page listing, and lightweight filtering over the existing browser model
- `browser-session-ergonomics.md`: current refinement slice for large-session readability, page-window controls, and navigation hints in the lightweight shell
- `large-entity-list-browsing.md`: current refinement slice for large entity-list sorting, windowing, mode selection, and clearer list-to-detail jumps

The next spec for this repo should continue refining presentation on top of the existing browser model rather than reopening shell, scaffolding, or core-data plumbing work.

## Rules

- keep parsing and domain logic in `eu5miner`
- keep new GUI work thin over stable `eu5miner.inspection` behavior
- make hosted CI sufficient for the default workflow
