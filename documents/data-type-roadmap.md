# Data Type Roadmap

## Purpose

This document maps the planned implementation order for EU5 game data types and related script families.

The ordering is driven by three factors:

1. Cross-cutting reuse across many systems.
2. Importance to real modding workflows.
3. Fit with the current parser maturity.

## Implementation Order

### 0. Foundation Layers

Already in progress or completed:

- source discovery
- merged virtual filesystem
- CST tokenization and grouping
- semantic object helpers
- CLI inspection tools

### 1. Reusable Scripted Logic

These are the highest-value first domain adapters because other systems depend on them.

Order:

1. scripted triggers
2. scripted effects
3. script values
4. scripted modifiers
5. scripted lists and scripted relations
6. on_actions and related hook definitions

### 2. Setup and Identity Definitions

These are foundational for country, culture, and religion-aware analysis.

Order:

1. setup countries
2. cultures and culture groups
3. religions and religion groups
4. country description categories and related setup helpers

### 3. Dynamic Content Systems

These are major modding surfaces and should be supported early.

Order:

1. events
2. missions
3. situations
4. disasters
5. customizable localization and effect/trigger localization helpers

Notes:

- Yes, situations should absolutely be on the roadmap. They are a major scripted gameplay object and belong early in the dynamic-content phase.
- Disasters are similarly important because they are heavily scripted and structurally close to other event-like systems.
- Situation research against the shipped EU5 files shows a mostly flat top-level object model with fields such as `monthly_spawn_chance`, `hint_tag`, `can_start`, `can_end`, `visible`, `on_start`, `on_monthly`, `on_ending`, `on_ended`, `tooltip`, `map_color`, and `secondary_map_color`.
- Some situations are simple single-phase lifecycle definitions, while others manage internal staged flow through variables and custom end-trigger helpers such as `*_end_trigger` flags checked from `can_end`.
- The first situation adapter should therefore model stable top-level lifecycle fields first and preserve the full semantic body for situation-specific internal state machines.

### 4. Economy and Production Systems

Order:

1. building types and building categories
2. goods, prices, and goods demand
3. production methods and employment systems
4. markets and related economic helpers

### 5. Diplomacy and Warfare Systems

Order:

1. casus belli and wargoals
2. peace treaties
3. subject types and subject military stances
4. country interactions and character interactions
5. unit types, unit abilities, and unit categories

### 6. Government and Society Systems

Order:

1. government types and reforms
2. laws and policies
3. estates and estate privileges
4. parliament types, agendas, and issues
5. institutions, holy sites, and religion-adjacent societal structures

### 7. Interface and Presentation Systems

Order:

1. localization bundles and cross-reference helpers
2. GUI script and scripted GUI
3. loading screen and main menu content helpers

### 8. Map and World Data

Order:

1. map text files such as `default.map`
2. map CSV helpers such as adjacencies and ports
3. location/setup cross-linking helpers
4. later image-assisted map assets if needed

### 9. Mod Project and Packaging

Order:

1. mod metadata and relationships
2. replace_paths and precedence-aware write planning
3. mod skeleton creation and targeted emission helpers

### 10. Library Integration Pass

After the major module-level adapters exist, do a single public API integration pass instead of stabilizing each domain in isolation.

Order:

1. audit module-level parser and model names across the library
2. define the stable package-level and domain-level export surface
3. align cross-domain naming and lookup patterns into one coherent model
4. update README and CLI-facing examples around the final integrated API

### 11. Broader Validation Sweep

Add a larger optional validation layer once the core domain adapters are in place.

Order:

1. add an optional slow test marker or dedicated test module for wide real-file coverage
2. parse a broader sample of files across `events`, `missions`, `situations`, `setup`, `common/scripted_*`, `gui`, and `map_data`
3. verify that representative adapters can load many files without crashing, hanging, or regressing on obvious structural expectations
4. keep this suite optional by default so the fast local development loop stays tight

## Near-Term Focus

The immediate sequence should be:

1. scripted triggers
2. scripted effects
3. setup countries
4. events
5. missions
6. situations

## Current Status

Implemented:

- scripted triggers
- scripted effects
- setup countries
- events
- missions
- situations
- disasters
- customizable localization and effect/trigger localization helpers
- localization bundles and cross-reference helpers
- GUI script and scripted GUI

Next recommended target:

- loading screen and main menu content helpers

This gives broad value quickly while staying aligned with the current parser architecture.
