# V1 Scope

Release `0.5.0` is a public preview inside this scope. It marks the first intentional public package cut, not the final `1.0` stability line.

## In Scope

- Project scaffold with strict typing and tests.
- Real-install discovery of the EU5 game root and phase roots.
- Readers and typed adapters for the major moddable text file families.
- Tests validated against representative real game files.
- Curated public package surfaces for library use and a thin CLI for inspection and reporting.
- Package structure designed for later parser and writer expansion.

## Out of Scope

- Binary savegame parsing.
- Binary art and engine files.
- Full mod overlay/write-back engine.
- Full semantic models for every EU5 gameplay domain.
- A frozen public API across every helper and integration surface.

## Preview Boundary

The preview release is expected to support real parsing and reporting work, but it does not yet claim that every helper surface is final. The first `1.0` release should follow a short hardening pass that confirms which import paths and workflows are part of the long-term compatibility contract.

## Intended 1.0 Contract Boundary

The intended `1.0` compatibility boundary is the current curated surface, not every helper exported anywhere in the package tree.

- The narrow root package: install discovery, VFS primitives, and the main mod workflow helpers.
- Grouped domain packages such as `eu5miner.domains.diplomacy`, `eu5miner.domains.economy`, `eu5miner.domains.government`, `eu5miner.domains.religion`, `eu5miner.domains.map`, `eu5miner.domains.localization`, and `eu5miner.domains.units` when working within one concept area.
- `eu5miner.inspection` for stable read-only install summaries, system reports, and the current narrow entity-browsing surface.
- `eu5miner.mods` for stable higher-level plan, apply, and report mod workflow operations.
- The CLI as a thin wrapper over those library seams rather than an expanded standalone product API.

The broad `eu5miner.domains` convenience import remains available during preview, but grouped packages are the preferred stable seam. Internal implementation modules and standalone convenience imports are not part of the preferred `1.0` contract.

## Why this cut

This scope captures the file families that matter most for modding and data mining while keeping the implementation small enough to stay test-heavy and extensible. It also avoids locking the project into brittle binary reverse engineering before the text core is reliable.
