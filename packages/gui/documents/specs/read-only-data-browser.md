# Spec: Read-Only Data Browser

## Objective

Advance the preview shell from a single formatted text dump into a thin browser model over stable `eu5miner.inspection` outputs.

## In Scope

- structured app/browser model for overview and report pages
- install overview page over `InstallSummary`
- per-system report pages over `SystemReport`
- shell and CLI wiring for browsing one or all supported reports from a selected install
- synthetic-fixture tests that stay independent from a real EU5 install

## Out Of Scope

- bespoke parser or VFS logic in this repo
- editing workflows
- heavyweight GUI frameworks or widget hierarchies
- install-required tests in the default validation path

## Acceptance Criteria

- the shell renders an install overview page and stable report pages from core APIs
- one CLI invocation can browse all supported reports for a single install
- the repo remains buildable and testable without a local game install
