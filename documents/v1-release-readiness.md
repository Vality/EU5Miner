# V1 Release Readiness

This document defines the narrow blocker set that should be green before proposing a real `1.0` release for the core library.

It is intentionally smaller than a full project roadmap. The goal is to confirm the already-curated compatibility boundary, not to reopen feature scope.

## Automated Gate

The following must stay green in the default no-install workflow:

- `uv run pytest`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

Within the test suite, these areas are the compatibility gate for the current curated seams:

- `tests/test_public_api.py` for the narrow root package, `eu5miner.inspection`, and `eu5miner.mods` export contracts
- `tests/test_grouped_package_api.py` for grouped domain package entrypoints
- `tests/test_inspection.py` for install-independent inspection and entity-browsing workflows
- `tests/test_mod_workflow_integration.py` for the stable mod planning, application, and CLI workflow behavior
- `tests/test_readme_contract_examples.py` for the documented root, inspection, and grouped-package examples that downstream users are told to copy

## Manual Check Before A Real Release Proposal

When a representative local EU5 install is available, run these sanity checks in addition to the automated gate:

- Run the documented install inspection and system-report workflows against the local install.
- Run the current mod planning or application workflow against a small representative mod workspace.
- Confirm downstream GUI and MCP work still consumes the documented core seams instead of internal modules.

## Non-Blockers

These are useful, but they are not part of the minimum `1.0` release gate:

- the optional broader sweep behind `uv run python -m pytest -m broad`
- new parser families or broader gameplay coverage
- new downstream product capabilities in GUI or MCP

If a proposed `1.0` doc change needs one of those items to become true, that is a scope gap and should be recorded explicitly instead of being folded into the gate.
