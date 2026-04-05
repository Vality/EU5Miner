# EU5MinerGUI

EU5MinerGUI is a dedicated application repo for a read-first GUI built on top of the core `eu5miner` library.

The current state is intentionally thin: this repo is being prepared for parallel cloud-agent work before committing to a larger UI stack.

## Status

- The repo is scaffolded as a standalone Python application.
- The first milestone is a launchable read-only shell that proves the dependency and validation pipeline.
- Substantial parsing and domain logic should continue to live in the `eu5miner` library, not here.

For now the dependency resolves directly from the `EU5Miner` GitHub repo so CI can run before a package-registry release exists.

The current shell stays thin over `eu5miner.inspection`: it can list the stable supported systems without a local install, and when given an install root it can render an install summary plus a selected stable system report such as `map`.

```powershell
eu5miner-gui
eu5miner-gui --install-root C:\EU5 --system map
```

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
