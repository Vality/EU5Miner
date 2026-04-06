# Spec: Browser Page Context

## Objective

Refine the lightweight read-only browser so each selected page better explains where it sits in the current session and how to recover when a report or entity page is unavailable.

## In Scope

- session-position hints for rendered overview, report, entity-list, and entity-detail pages
- previous and next page-key hints over the already-loaded browser session
- clearer unavailable-page guidance that points users back to the overview and explains why unavailable pages remain indexed
- synthetic-fixture tests that remain independent from a real EU5 install

## Out Of Scope

- parser, VFS, or domain-model behavior in this repo
- interactive widgets or keyboard-driven navigation
- core-library pagination or search APIs
- install-required tests in the default validation path

## Acceptance Criteria

- rendered pages show their session position within the current loaded browser session
- rendered pages expose previous or next page keys when neighboring pages exist
- unavailable pages explain how to recover context from the overview and why they still appear in partial-install sessions