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

## Why this cut

This scope captures the file families that matter most for modding and data mining while keeping the implementation small enough to stay test-heavy and extensible. It also avoids locking the project into brittle binary reverse engineering before the text core is reliable.
