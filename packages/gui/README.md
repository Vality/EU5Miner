# EU5MinerGUI

EU5MinerGUI is an unofficial companion application repo built on top of the core `eu5miner` library for Europa Universalis V data inspection.

Release `0.6.0` is the current public preview release for this repo.

This project is not affiliated with, endorsed by, or sponsored by Paradox Interactive. No game files or other game assets are included in this repository or its built artifacts.

## Status

The `0.6.x` line should be treated as a public preview.

- The repo ships a standalone Python application package and command entrypoint.
- The current surface is a read-only text shell over stable core browse seams, including inspection-backed install overview, system reports, covered entity list/detail browsing, thin diplomacy helper pages built over grouped `eu5miner.domains.diplomacy` helpers, and one thin religion helper page built over grouped `eu5miner.domains.religion` helpers.
- GUI-specific product work should continue here, while parsing, VFS, and domain-model logic stay in the core `eu5miner` library.

The published dependency is pinned to the coordinated core `eu5miner` release tag `v0.6.0`. In this multi-repo workspace, local `uv` resolution still points `eu5miner` at the sibling `../EU5Miner` checkout so GUI validation follows the checked-out core source during coordinated workspace work.

Release `0.6.0` captures the completed step-2 grouped-helper breadth for the current preview line: diplomacy helper pages and the single religion helper page are both shipped, and that helper scope remains explicit. The immediate post-release phase is validation, build, test, and preview-contract maintenance for later patch or minor planning rather than widening helper scope again.

## Current Browser Shell

The current preview command prints a structured read-only browser view backed by stable core browse seams.

- Without a local install, it renders the overview page with the supported system list and an unloaded install-summary section.
- With `--install-root`, it renders an install overview page with roots, phases, and merged content sources.
- With both `--install-root` and `--system`, it loads the selected stable system report page, such as `map`, and focuses that page by default.
- With `--install-root` and `--entity-system`, it loads an entity list page for one currently browseable inspection system, such as `diplomacy`, `religion`, or `map`.
- With `--install-root --entity-system ... --entity ...`, it loads the corresponding entity detail page with generic fields and cross-system references from `eu5miner.inspection`.
- With `--install-root --diplomacy-helper war-flow` or `diplomacy-graph`, it loads a thin helper report page backed by representative install files plus grouped `eu5miner.domains.diplomacy` helper builders.
- With `--install-root --religion-helper religion-overview`, it loads a thin summary helper report page backed by representative install files plus grouped `eu5miner.domains.religion` catalog and report builders.
- Entity list pages now sort by entity name by default, keep their own explicit entity window, and can switch between compact rows and detail rows with embedded detail-page keys.
- Use `--entity-list-sort`, `--entity-list-limit`, `--entity-list-offset`, and `--entity-list-mode` when large covered systems need a narrower or more detail-oriented list view.
- With `--page`, the shell can focus a page key directly: `overview` or `home`, `report:map` or `system:map`, `entities:religion` or `list:religion`, `helper:war-flow` or `diplomacy-helper:war-flow`, `helper:religion-overview` or `religion-helper:religion-overview`, or `entity:map:stockholm` or `detail:map:stockholm`.
- With `--list-pages`, it prints only the current page index; with `--page-filter`, it narrows loaded pages by case-insensitive text across page metadata and rendered lines.
- The page index now windows large sessions by default. Use `--page-list-limit`, `--page-list-offset`, or `0` to disable page-index truncation when you need a wider index dump.
- The shell header now prints a compact session summary with loaded, ready, and unavailable page counts plus the current browse request scope, so page-focused views keep their broader session context.
- Rendered page sections still truncate long generic sections by default. Use `--section-line-limit 0` for full non-entity output, while entity list pages use their own entity-window controls instead of the generic section truncation.
- With `--install-root --all-systems`, it loads one install overview, all supported report pages, and all current browseable entity list pages exposed by `eu5miner.inspection`, while still rendering only the selected page by default.
- `--show-all-pages` restores the full multi-page dump when you want to inspect the whole loaded session at once.
- Rendered pages now include lightweight navigation hints such as the current page key, session position, neighboring page keys, overview page, related list page, or detail-page pattern.
- Rendered pages now also include concrete CLI reopen hints for the current page, including direct `--page ...` targets and matching `--system` or `--entity-system/--entity` selection flags when available.
- Entity list pages now also surface visible detail-page examples so you can jump directly from a large list page into specific entity detail pages.
- When a selected install is partial or synthetic, the browser keeps the overview and marks unavailable system pages instead of aborting the whole session, while unavailable pages now explain how to recover context from the overview.

```powershell
eu5miner-gui
eu5miner-gui --install-root C:\EU5 --system map
eu5miner-gui --install-root C:\EU5 --entity-system religion
eu5miner-gui --install-root C:\EU5 --entity-system religion --entity-list-limit 10 --entity-list-offset 20
eu5miner-gui --install-root C:\EU5 --entity-system government --entity-list-mode detail
eu5miner-gui --install-root C:\EU5 --entity-system economy --entity-list-sort group
eu5miner-gui --install-root C:\EU5 --entity-system map --entity stockholm
eu5miner-gui --install-root C:\EU5 --diplomacy-helper war-flow
eu5miner-gui --install-root C:\EU5 --religion-helper religion-overview
eu5miner-gui --install-root C:\EU5 --page helper:diplomacy-graph
eu5miner-gui --install-root C:\EU5 --page religion-helper:religion-overview
eu5miner-gui --install-root C:\EU5 --page report:map
eu5miner-gui --install-root C:\EU5 --page system:map
eu5miner-gui --install-root C:\EU5 --page detail:government:monarchy
eu5miner-gui --install-root C:\EU5 --all-systems --list-pages
eu5miner-gui --install-root C:\EU5 --all-systems --page-list-limit 5
eu5miner-gui --install-root C:\EU5 --all-systems --page-filter map
eu5miner-gui --install-root C:\EU5 --all-systems
eu5miner-gui --install-root C:\EU5 --all-systems --show-all-pages
```

Page filtering works only over pages already loaded into the current browser session. Use `--all-systems` or the relevant explicit selection flags when you want a wider index before filtering. If a filter matches nothing, the shell now calls that out explicitly and reminds you that filtering only applies to the loaded session.

Install-backed reporting requires your own local EU5 installation. This repo does not bundle sample game content.

## Development

Initialize the centralized environment with:

```powershell
.\scripts\setup-centralized-uv.ps1
```

Run the standard checks:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

Inside this workspace, `uv` resolves `eu5miner` from the sibling core checkout. That keeps GUI tests and shell output aligned with the latest `eu5miner.inspection` supported-system and entity-browsing contract during post-release coordination and later patch planning.
The published package metadata remains pinned to the coordinated core `v0.6.0` release tag even when local workspace validation uses the sibling checkout override.

## Documentation

- Planning entrypoint: [ROADMAP.md](ROADMAP.md)
- Execution-ready specs: [documents/specs/README.md](documents/specs/README.md)
- Architecture notes: [documents/architecture.md](documents/architecture.md)
- Environment notes: [documents/development-environment.md](documents/development-environment.md)
