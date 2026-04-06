# Preview Alignment With Core Inspection Contract

## Objective

Keep the GUI preview in lockstep with the stable `eu5miner.inspection` contract so core preview changes land here as intentional doc and test updates instead of reopened browse-refinement work.

## In Scope

- focused GUI-side contract coverage for supported-system and browseable-entity-system ordering, names, and descriptions
- page-order and shell-output checks that depend on the core inspection catalog, especially the `--all-systems` flow
- checked-in GUI docs and examples that enumerate supported systems, browseable entity systems, or preview-alignment behavior
- workspace preview alignment notes around the published core dependency and local `[tool.uv.sources]` override

## Out Of Scope

- new browser ergonomics, navigation, filtering, or page-context features
- parser, VFS, or domain-model logic in this repo
- editing workflows or GUI framework expansion
- install-required validation in the default workflow

## Planned Changes

- add one focused GUI contract seam, either in `tests/test_gui_shell.py` or a dedicated companion test module, that fails clearly when the core inspection catalog changes
- assert that GUI helpers and `--all-systems` page loading continue to derive report and entity-list ordering from `eu5miner.inspection` rather than GUI-local copies
- update GUI docs in the same slice whenever the core contract changes any supported-system or browseable-entity-system names, descriptions, or preview-alignment guidance
- keep roadmap and spec-index language pointed at alignment work so landed browse refinements remain closed baseline scope

## Acceptance Criteria

- a focused GUI test seam verifies the current supported-system and browseable-entity-system contract exposed by `eu5miner.inspection`
- the loaded page order for `--all-systems` remains `overview`, then report pages in supported-system order, then entity-list pages in browseable-entity-system order
- checked-in GUI docs that describe preview alignment or enumerate inspection-backed systems are updated alongside any core contract change
- the next GUI slice does not reopen browse ergonomics unless a core contract change forces a narrow follow-up

## Validation

- `uv run pytest`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`
- verify planned assertions against the sibling core contract in `../EU5Miner/tests/test_inspection_contract.py`
