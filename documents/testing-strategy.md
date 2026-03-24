# Testing Strategy

## Core Principle

Tests are part of the product design. The library should be built against real EU5 files from the installed game so parser and discovery logic reflect the game as shipped.

## Test Categories

### Real-install tests

These tests should run against the local EU5 install when present.

They validate:

- install discovery
- expected phase roots
- representative file presence
- basic structural parsing of real files

### Unit tests

These tests validate smaller helper behavior using short inline examples.

They validate:

- path resolution
- script construct detection
- localization parsing
- CSV parsing
- metadata parsing

### Future golden tests

As the CST and writer arrive, the suite should add:

- parse-tree golden tests
- round-trip serialization tests
- local-format-preservation tests
- overlay precedence tests

## Real-File Policy

- Prefer tests that validate the parser against representative shipped files.
- Keep the test corpus centered on the major moddable text file families.
- Skip real-install tests cleanly if the install is unavailable.
