# EU5Miner Specification

## Purpose

EU5Miner is a Python library for parsing Europa Universalis V game data and mods for two primary use cases:

1. Data mining and indexing.
2. Mod creation, inspection, and safe editing.

## Version 1 Goals

The first release is intentionally limited to the major moddable text-based file families and the infrastructure needed to support them well.

Included in scope:

- Install and content-root discovery for vanilla EU5 content.
- Source modeling for vanilla files, DLC-like content, and mods.
- Awareness of EU5 phase loading order: `loading_screen`, `main_menu`, `in_game`.
- Readers for representative text families: script text, GUI text, localization YAML, JSON metadata, and semicolon CSV.
- Test-heavy validation against real installed game files.
- An extensible package structure that supports later CST, AST, typed models, overlay logic, and write-back.

Excluded from v1:

- Binary asset parsing such as `.dds`, `.schematic`, `.editordata`, and `nodes.dat`.
- Patch-sensitive binary savegame decoding.
- A full editing and formatting-preserving writer for Clausewitz text.

## Non-Functional Requirements

- Python 3.12+
- Mypy-typed code
- Ruff linting
- Pytest-driven development
- Tests should use real EU5 files where practical
- Public APIs should remain small and extensible

## Current Curated Public API Direction

The current intended `1.0` boundary is the curated surface that the preview docs already point downstream users toward:

- The narrow `eu5miner` root package for install discovery, VFS primitives, and the main mod workflow helpers.
- Grouped domain packages such as `eu5miner.domains.diplomacy`, `eu5miner.domains.economy`, `eu5miner.domains.government`, `eu5miner.domains.religion`, `eu5miner.domains.map`, `eu5miner.domains.localization`, and `eu5miner.domains.units` for concept-local imports.
- `eu5miner.inspection` for stable read-only install summaries, system reports, and the current narrow entity-browsing workflow.
- `eu5miner.mods` for stable plan, apply, and report mod workflow operations.
- The CLI as a thin wrapper over those library seams, not as a broader standalone product API.

The broad `eu5miner.domains` convenience import remains available during preview, but grouped packages are the preferred stable seam. Internal implementation modules are not part of the intended compatibility contract.
