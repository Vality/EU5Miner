# Changelog

## Unreleased

No unreleased changes recorded after `0.6.0`.

## 0.6.0 - 2026-04-06

- Added a substantially broader read-only inspection facade: downstream callers can now list supported entity-browsing systems, enumerate entities, and fetch detailed entities for the initial economy, diplomacy, government, religion, and map families.
- Locked the intended preview compatibility boundary with focused contract coverage for `eu5miner.inspection`, grouped domain packages, the thin CLI command surface, README examples, and the higher-level `eu5miner.mods` workflow.
- Added explicit `python -m eu5miner` and wheel `__main__` entrypoints so packaged CLI execution matches the documented thin command surface.
- Cleaned the default no-install validation baseline so `uv run pytest` stays warning-free even without optional plugins, and added release-readiness docs for the later `1.0` proposal.
- Refreshed README, roadmap, spec-index, scope, security, and environment wording so the checked-in preview state and OneDrive-safe `uv` workflow stay consistent across the repo.

## 0.5.0 - 2026-03-28

- First public preview release.
- Install discovery, virtual filesystem helpers, generic text-family parsing, and typed domain adapters are available from the published package.
- The CLI includes install inspection, representative parsing, system reporting, and the current mod update planning and application workflow.
- Representative-file tests, strict typing, and focused integration coverage are in place across the implemented parser and domain layers.
- API stabilization is still in progress ahead of a later `1.0` release.
