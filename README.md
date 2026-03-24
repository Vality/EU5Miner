# EU5Miner

EU5Miner is a text-first Python library for reading, indexing, and eventually editing Europa Universalis V data and mod files.

The initial implementation focuses on the major moddable text-based file families:

- Clausewitz-style script text used in `common`, `events`, `setup`, and `map_data`
- GUI script
- Localization YAML
- JSON metadata
- Semicolon-delimited CSV

The project is intentionally test-heavy. Early functionality is validated against real EU5 install files so later parser work is anchored in observed game behavior instead of assumptions.

## Development

This repository is stored under OneDrive, so the recommended setup is to keep the `uv` environment outside the synced tree.

Initialize or refresh the centralized environment with:

```powershell
.\scripts\setup-centralized-uv.ps1
```

That script points `UV_PROJECT_ENVIRONMENT` at `%USERPROFILE%\.venvs\EU5Miner` and runs `uv sync --extra dev` there.

If you need a one-off local setup instead, install development dependencies with `uv`:

```powershell
uv sync --extra dev
```

Run the initial checks:

```powershell
$env:UV_PROJECT_ENVIRONMENT = "$env:USERPROFILE\.venvs\EU5Miner"
uv run pytest
uv run ruff check .
uv run mypy src
```

If `uv run` still fights filesystem behavior in the synced folder, the project-local fallback remains:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src
```

## CLI

The project now ships a thin CLI:

```powershell
eu5miner inspect-install
eu5miner list-files --phase in_game --subpath gui --limit 10
eu5miner analyze-script --representative scripted_trigger
```

## Testing

The suite includes timeout protection for parser-sensitive tests so future performance regressions fail quickly instead of appearing to hang indefinitely.

## Configuration

The test suite and install-discovery helpers use this precedence for the game install path:

1. `EU5_INSTALL_DIR`
2. The default Steam install path on Windows

## Documentation

Design and research notes are stored in [documents/specification.md](documents/specification.md) and the other files in `documents/`.

Developer environment notes for the OneDrive/`uv` workflow are in [documents/development-environment.md](documents/development-environment.md).

The planned game-data implementation order is tracked in [documents/data-type-roadmap.md](documents/data-type-roadmap.md).
