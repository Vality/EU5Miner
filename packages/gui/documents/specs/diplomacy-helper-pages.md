# Spec: Diplomacy Helper Pages

## Objective

Broaden the read-only shell beyond the inspection report and entity subset by exposing thin diplomacy helper pages backed directly by stable grouped `eu5miner.domains.diplomacy` helpers and representative install files.

## In Scope

- one explicit helper-page family in the existing browser model and CLI flow
- representative install file loading through the core `GameInstall` seam
- helper summaries for the `war-flow` and `diplomacy-graph` diplomacy helpers
- focused synthetic-install tests that prove the GUI stays thin over core grouped-package helpers

## Out Of Scope

- new parser, VFS, or domain-model logic in this repo
- widening `--all-systems` into a generic helper loader
- bespoke GUI widgets or a replacement for the current text-first browser model
- editing workflows or install-required validation in the default workflow

## Acceptance Criteria

- the shell can render `helper:war-flow` and `helper:diplomacy-graph` pages from a selected install
- the CLI exposes explicit helper selection without duplicating diplomacy parsing logic in the GUI repo
- helper pages derive their content from grouped `eu5miner.domains.diplomacy` builders over representative install files
- the repo remains buildable and testable without a local EU5 install

## Validation

- `uv run pytest tests/test_gui_shell.py`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`