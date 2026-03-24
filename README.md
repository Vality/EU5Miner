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

Install development dependencies with `uv`:

```powershell
uv sync --extra dev
```

Run the initial checks:

```powershell
uv run pytest
uv run ruff check .
uv run mypy src
```

## Configuration

The test suite and install-discovery helpers use this precedence for the game install path:

1. `EU5_INSTALL_DIR`
2. The default Steam install path on Windows

## Documentation

Design and research notes are stored in [documents/specification.md](documents/specification.md) and the other files in `documents/`.
