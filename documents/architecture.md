# Architecture

## Layering

The project should evolve in four layers:

1. Source discovery and virtual filesystem.
2. Text-family readers and analyzers.
3. Concrete syntax tree and stable writer for script-like formats.
4. Higher AST and typed domain models.

The current implementation starts with layers 1 and 2.

## Source Model

The core install model should expose:

- The game root.
- The `game` directory.
- The content phase roots.
- DLC roots when needed later.

This layer should eventually generalize to workshop mods, local mods, and overlay resolution.

## Extensibility Principles

- Keep file-family readers separate from source discovery.
- Return typed dataclasses instead of raw dictionaries where practical.
- Preserve enough structure in early readers to inform later parser and writer work.
- Keep public APIs narrow until real usage patterns emerge from tests.

## Initial Modules

- `eu5miner.paths`: install path resolution.
- `eu5miner.source`: install discovery and phase-based file enumeration.
- `eu5miner.vfs`: merged source modeling, provenance, and phase-aware file precedence.
- `eu5miner.formats.script_text`: structural script analysis.
- `eu5miner.formats.localization`: localization file reader.
- `eu5miner.formats.map_csv`: semicolon CSV reader.
- `eu5miner.formats.metadata`: JSON metadata reader.
