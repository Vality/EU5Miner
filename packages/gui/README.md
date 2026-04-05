# EU5MinerGUI

EU5MinerGUI is an unofficial companion application repo built on top of the core `eu5miner` library for Europa Universalis V data inspection.

Release `0.5.0` is the first public preview release for this repo.

This project is not affiliated with, endorsed by, or sponsored by Paradox Interactive. No game files or other game assets are included in this repository or its built artifacts.

## Status

The `0.5.x` line should be treated as a public preview.

- The repo ships a standalone Python application package and command entrypoint.
- The current surface is a read-only text shell over stable `eu5miner.inspection` APIs, not a graphical browser yet.
- GUI-specific product work should continue here, while parsing, VFS, and domain-model logic stay in the core `eu5miner` library.

The current preview is pinned to the core `eu5miner` `v0.5.0` release tag and follows that preview contract rather than tracking the moving `main` branch.

## Current Browser Shell

The current preview command prints a structured read-only browser view backed by the stable `eu5miner.inspection` APIs.

- Without a local install, it renders an overview page with the supported system list and an unloaded install-summary section.
- With `--install-root`, it renders an install overview page with roots, phases, and merged content sources.
- With both `--install-root` and `--system`, it adds the selected stable system report page, such as `map`.
- With `--install-root --all-systems`, it renders one install overview plus all supported report pages in a single browseable shell output.
- When a selected install is partial or synthetic, the browser keeps the overview and marks unavailable system pages instead of aborting the whole session.

```powershell
eu5miner-gui
eu5miner-gui --install-root C:\EU5 --system map
eu5miner-gui --install-root C:\EU5 --all-systems
```

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
