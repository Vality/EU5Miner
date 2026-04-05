# EU5MinerGUI

EU5MinerGUI is an unofficial companion application repo built on top of the core `eu5miner` library for Europa Universalis V data inspection.

Release `0.5.0` is the first public preview release for this repo.

This project is not affiliated with, endorsed by, or sponsored by Paradox Interactive. No game files or other game assets are included in this repository or its built artifacts.

## Status

The `0.5.x` line should be treated as a public preview.

- The repo ships a standalone Python application package and command entrypoint.
- The current surface is a read-only text shell over stable `eu5miner.inspection` APIs, including install overview, system reports, and covered entity list/detail browsing.
- GUI-specific product work should continue here, while parsing, VFS, and domain-model logic stay in the core `eu5miner` library.

This workspace slice currently tracks the core `eu5miner` `main` branch so the GUI can consume the new inspection entity-browsing seam ahead of the next preview release.

## Current Browser Shell

The current preview command prints a structured read-only browser view backed by the stable `eu5miner.inspection` APIs.

- Without a local install, it renders the overview page with the supported system list and an unloaded install-summary section.
- With `--install-root`, it renders an install overview page with roots, phases, and merged content sources.
- With both `--install-root` and `--system`, it loads the selected stable system report page, such as `map`, and focuses that page by default.
- With `--install-root` and `--entity-system`, it loads an entity list page for one covered system: `economy`, `government`, `religion`, or `map`.
- With `--install-root --entity-system ... --entity ...`, it loads the corresponding entity detail page with generic fields and cross-system references from `eu5miner.inspection`.
- With `--page`, the shell can focus a page key directly: `overview`, `report:map`, `entities:religion`, or `entity:map:stockholm`.
- With `--list-pages`, it prints only the current page index; with `--page-filter`, it narrows loaded pages by case-insensitive text across page metadata and rendered lines.
- With `--install-root --all-systems`, it loads one install overview, all supported report pages, and all covered entity list pages, while still rendering only the selected page by default.
- `--show-all-pages` restores the full multi-page dump when you want to inspect the whole loaded session at once.
- When a selected install is partial or synthetic, the browser keeps the overview and marks unavailable system pages instead of aborting the whole session.

```powershell
eu5miner-gui
eu5miner-gui --install-root C:\EU5 --system map
eu5miner-gui --install-root C:\EU5 --entity-system religion
eu5miner-gui --install-root C:\EU5 --entity-system map --entity stockholm
eu5miner-gui --install-root C:\EU5 --page report:map
eu5miner-gui --install-root C:\EU5 --all-systems --list-pages
eu5miner-gui --install-root C:\EU5 --all-systems --page-filter map
eu5miner-gui --install-root C:\EU5 --all-systems
eu5miner-gui --install-root C:\EU5 --all-systems --show-all-pages
```

Page filtering works only over pages already loaded into the current browser session. Use `--all-systems` or the relevant explicit selection flags when you want a wider index before filtering.

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

## Documentation

- Planning entrypoint: [ROADMAP.md](ROADMAP.md)
- Execution-ready specs: [documents/specs/README.md](documents/specs/README.md)
- Architecture notes: [documents/architecture.md](documents/architecture.md)
- Environment notes: [documents/development-environment.md](documents/development-environment.md)
