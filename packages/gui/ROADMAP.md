# EU5MinerGUI Roadmap

This roadmap is intentionally short. The GUI repo should stay focused on UI and product-surface work, not on reimplementing library logic.

## Current Order

### 1. Foundation And Repo Alignment

Goal: establish the repo, package, CI, docs, and app entrypoint.

### 2. Read-Only Application Shell

Goal: launch a minimal GUI shell that can show placeholder content driven by stable `eu5miner` imports.

### 3. Read-Only Data Browsing

Goal: browse parsed definitions, reports, and linked summaries from the library.

### 4. Editing Workflows

Goal: only after the library seam is stable enough, add editing and mod-write workflows.

## Rules

- parsing work stays in `eu5miner`
- UI work stays here
- major feature slices should be backed by a spec in `documents/specs/`
