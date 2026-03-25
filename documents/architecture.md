# Architecture

## Layering

The project should evolve in four layers:

1. Source discovery and virtual filesystem.
2. Text-family readers and analyzers.
3. Concrete syntax tree and stable writer for script-like formats.
4. Higher AST and typed domain models.

The current implementation starts with layers 1 and 2.

The current parser work now includes a minimal CST tokenizer layer, first-pass structural grouping for top-level statements, scalar values, and blocks, and a semantic helper layer for object-like definitions and key/value access. This keeps the model useful for inspection while staying small enough to refine against real game files.

The next layer can now be domain adapters that interpret specific semantic patterns such as scripted triggers, scripted effects, setup-country definitions, and event definitions without forcing the generic CST or semantic layers to become game-specific.

## Source Model

The core install model should expose:

- The game root.
- The `game` directory.
- The content phase roots.
- DLC roots when needed later.

This layer should eventually generalize to workshop mods, local mods, and overlay resolution.

The virtual filesystem layer now also needs to carry metadata-derived precedence rules such as `replace_path`, because source ordering alone is not enough to model subtree replacement correctly. That same precedence model should drive write planning at exact-file, subtree, intended-emission, and mod-metadata-update levels so edit targets can be evaluated against higher-priority exact-file and replace-path blockers, so callers can tell when full subtree ownership would require a new `replace_path`, and so higher-level tools can derive concrete recommendations such as create, keep, override, blocked, or add-replace-path. A thin mod-project layer can then sit above that planning output to derive skeleton directories, metadata.json handling, deterministic write payloads, and eventually actual filesystem materialization helpers.

## Extensibility Principles

- Keep file-family readers separate from source discovery.
- Return typed dataclasses instead of raw dictionaries where practical.
- Preserve enough structure in early readers to inform later parser and writer work.
- Keep public APIs narrow until real usage patterns emerge from tests.

## Initial Modules

- `eu5miner.paths`: install path resolution.
- `eu5miner.source`: install discovery and phase-based file enumeration.
- `eu5miner.vfs`: merged source modeling, provenance, and phase-aware file precedence.
- `eu5miner.formats.cst`: tokenization and first-pass CST document model with statements, scalar values, and blocks for Clausewitz-style text.
- `eu5miner.formats.semantic`: semantic helpers for object-like definitions, key/value access, and reusable entry lookup on top of the CST.
- `eu5miner.domains`: domain adapters for specific EU5 data families such as scripted triggers, scripted effects, setup countries, and later events, missions, and situations.
- `eu5miner.formats.script_text`: structural script analysis.
- `eu5miner.formats.localization`: localization file reader.
- `eu5miner.formats.map_csv`: semicolon CSV reader.
- `eu5miner.formats.metadata`: JSON metadata reader.
