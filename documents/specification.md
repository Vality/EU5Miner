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

## Initial Public API Direction

The initial code should support:

- Discovering the EU5 install and its major content roots.
- Enumerating files under content phases.
- Reading representative file families into minimal structured models.
- Detecting script-level constructs needed by later parser work.
