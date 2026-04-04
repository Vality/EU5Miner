# EU5MinerGUI Agent Guide

## Purpose

This repository is for the GUI application that sits on top of the core `eu5miner` library.

Agents working here should optimize for:

- keeping GUI-specific code in this repo and parser or domain logic in `eu5miner`
- small, typed, test-backed increments
- app-shell and UI work that can validate without a local EU5 install

## Start Here

Read these documents first:

1. `README.md`
2. `ROADMAP.md`
3. `documents/specs/README.md`
4. `documents/architecture.md`
5. `documents/development-environment.md`

## Working Norms

- Treat `eu5miner` as the source of truth for parsing, VFS, and typed domain models.
- Keep this repo thin over stable library APIs.
- Prefer a read-only browsing shell before adding editing workflows.
- Keep validation green in hosted CI without requiring a game install.
