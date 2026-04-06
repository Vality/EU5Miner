# Spec Index

These specs are the execution layer under `ROADMAP.md`.

## Current Status

The shell, browser, and browse-refinement specs in this folder now describe landed preview behavior. The first two explicit checked step-2 implementation slices are the diplomacy helper page family over the stable grouped core diplomacy package and the single-page religion helper follow-on over the stable grouped core religion package.

The 0.6.0 preview cut now also packages the step-3 coherence sweep after that shipped step-2 breadth. No additional helper-page breadth is the current active spec; the next major phase is operational and release-oriented.

## Landed Baseline Specs

- `read-only-shell.md`: completed foundation for the launchable app shell and CLI entrypoint
- `read-only-data-browser.md`: completed baseline for the structured overview and per-system report browser model
- `entity-browser-pages.md`: completed browse refinement for covered entity list/detail pages over `eu5miner.inspection`
- `browser-navigation.md`: completed navigation refinement for explicit page focus, page listing, and lightweight filtering over the existing browser model
- `browser-session-ergonomics.md`: completed refinement for large-session readability, page-window controls, and navigation hints in the lightweight shell
- `large-entity-list-browsing.md`: completed refinement for large entity-list sorting, windowing, mode selection, and clearer list-to-detail jumps
- `browser-page-context.md`: completed refinement for session-position hints, unavailable-page recovery guidance, and hidden-selection reopen hints over the loaded browser session
- `diplomacy-helper-pages.md`: completed first checked step-2 slice for thin `war-flow` and `diplomacy-graph` helper pages over the stable `eu5miner.domains.diplomacy` grouped package
- `religion-helper-pages.md`: completed second checked step-2 slice for one thin `religion-overview` helper page over the stable `eu5miner.domains.religion` grouped package

Treat the browse-refinement specs above as closed baseline scope. Reopen them only when a core contract change forces a narrow follow-up.

## Current Release-Readiness Focus

- `preview-alignment.md`: reference slice for keeping GUI tests, docs, and `--all-systems` behavior aligned with the stable `eu5miner.inspection` supported-system and browseable-entity-system contract while release-readiness work proceeds

The next major phase is full validation, build, test, and preview release readiness over the shipped browser and helper-page surface. Future helper-page follow-ons should stay as narrow as the shipped diplomacy and religion slices instead of turning helper pages into a generic second browse surface.

## Rules

- keep parsing and domain logic in `eu5miner`
- keep new GUI work thin over stable `eu5miner.inspection` behavior
- make hosted CI sufficient for the default workflow
