# V1 Scope

## In Scope

- Project scaffold with strict typing and tests.
- Real-install discovery of the EU5 game root and phase roots.
- Initial readers for the major moddable text file families.
- Tests validated against representative real game files.
- Package structure designed for later parser and writer expansion.

## Out of Scope

- Binary savegame parsing.
- Binary art and engine files.
- Full mod overlay/write-back engine.
- Full semantic models for every EU5 gameplay domain.

## Why this cut

This scope captures the file families that matter most for modding and data mining while keeping the implementation small enough to stay test-heavy and extensible. It also avoids locking the project into brittle binary reverse engineering before the text core is reliable.
