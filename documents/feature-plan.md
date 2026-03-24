# Feature Plan

## Objective

The next development sequence should follow the order already established:

1. Merged virtual filesystem with provenance and phase-aware precedence.
2. CST parser core for Clausewitz-style text.
3. Thin CLI for install inspection and diagnostics.

This order keeps the work test-heavy and extensible. The parser should operate on a source model that already reflects real EU5 load behavior, and the CLI should sit on top of stable library APIs rather than driving design prematurely.

## Feature 1: Merged Virtual Filesystem

### Goal

Represent vanilla game content, DLC-like content, and mod-like content as explicit sources and expose merged file views with provenance.

### Deliverables

- A source descriptor for vanilla, DLC, and mod roots.
- Phase-aware file enumeration for `loading_screen`, `main_menu`, and `in_game`.
- Merged file lookup keyed by relative phase path.
- Provenance tracking showing every contributing source for a merged path.
- Explicit precedence ordering where the last source wins at the file level.

### Testing

- Synthetic precedence tests using temporary source roots.
- Real-install tests proving vanilla and DLC sources are discovered.
- Tests confirming representative paths can be located through the merged view.

## Feature 2: CST Parser Core

### Goal

Start the real text parser with a tokenizer and a minimal concrete syntax tree model that preserves source order and can support round-trip writing later.

### Deliverables

- Token model for identifiers, strings, braces, operators, comments, and expression markers.
- Tokenizer for Clausewitz-style script text.
- Minimal document node preserving the token stream and source text span information.
- Parser entry point for turning text into a lightweight CST document.

### Testing

- Inline tokenizer tests for macros, comments, braces, and scoped identifiers.
- Real-file smoke tests using representative EU5 script files.
- Structural tests proving token streams remain balanced on known-good files.

## Feature 3: Thin CLI

### Goal

Provide a minimal command-line layer that exposes stable inspection workflows without locking the library into a large command surface.

### Deliverables

- `inspect-install` style command for showing the discovered install and phase roots.
- `list-files` style command for phase-aware file listing from the merged VFS.
- `analyze-script` style command for running the initial parser diagnostics.

### Testing

- Command smoke tests on synthetic inputs.
- Real-install smoke test for install inspection when EU5 is available.

## Execution Notes

- Each feature should land with tests and docs updates in the same change set.
- Real-file validation remains mandatory wherever feasible.
- Public APIs should remain narrow until usage patterns emerge from tests and parser work.
