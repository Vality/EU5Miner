# Research Findings

## Important Learnings

### 1. EU5 content is phase-loaded

The installed game content is organized into three top-level phase folders:

- `loading_screen`
- `main_menu`
- `in_game`

These appear both in the base game and in official modding documentation. Any library that models file precedence or mod behavior must treat them as first-class concepts.

### 2. The most important moddable files are text-based

The initial high-value file families are:

- Clausewitz/Jomini-style script text in `common`, `events`, `setup`, and `map_data`
- GUI script in `.gui` files
- Localization `.yml`
- JSON metadata
- Semicolon-delimited CSV tables

This supports a strong v1 without depending on binary reverse engineering.

### 3. Representative install coverage

Early validation should cover a small set of representative files across the major text families: script text, setup data, GUI, map data, localization, and metadata.

The concrete sample list should live in code so it can evolve with the parser surface without turning this document into a stale inventory.

### 4. Mod structure is strict

Official documentation and the shipped layout agree on these rules:

- Mods mirror the structure under the game's `game/` directory.
- Mods require a `.metadata/metadata.json` file.
- Whole-file overrides are important.
- Database entry modes like `INJECT:key` and `REPLACE:key` must be modeled.

### 5. Generated docs are useful but optional

The official guidance points modders at `script_docs` and `dump_data_types`, but those generated files may be absent in a given install or tooling setup. The library should treat them as optional schema inputs, not hard dependencies.

### 6. Binary support should be deferred

Binary savegames and binary engine formats are patch-sensitive and not required to deliver value for the initial text-first library. They should remain future work or optional extension modules.
