# EU5Miner

A modular toolkit for working with Europa Universalis V game data, published as three coordinated Python packages from this single uv workspace.

## Packages

- **[`eu5miner`](packages/core/)** — Core library and CLI. Pure-Python, no runtime deps beyond the stdlib. Provides the data model, format readers, inspection utilities, and the `eu5miner` command-line entrypoint.
- **[`eu5miner-mcp`](packages/mcp/)** — Model Context Protocol server exposing EU5Miner data to LLMs. CLI: `eu5miner-mcp`.
- **[`eu5miner-gui`](packages/gui/)** — Desktop UI for browsing EU5 data. Built on Kivy. CLIs: `eu5miner-gui`, `eu5miner-gui-shell`.

## Install

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
# Core only (library + CLI)
pip install eu5miner

# Add MCP support (pulls in eu5miner-mcp)
pip install eu5miner[mcp]

# Add GUI support (pulls in eu5miner-gui)
pip install eu5miner[gui]

# Everything
pip install eu5miner[all]
```

Each package is also independently installable:

```bash
pip install eu5miner-mcp
pip install eu5miner-gui
```

## Development

This is a uv workspace. Clone and sync once:

```bash
git clone https://github.com/Vality/EU5Miner.git
cd EU5Miner
uv sync --all-packages --extra=dev
```

Run tests, lint, type checks per package:

```bash
cd packages/core && uv run pytest
cd ../mcp && uv run pytest
cd ../gui && uv run pytest

uv run ruff check .
uv run mypy packages/core/src packages/mcp/src packages/gui/src
```

Build all three wheels:

```bash
uv build --all-packages
```

A Windows setup script is provided at `scripts/setup-centralized-uv.ps1` for users who prefer a centralized venv under `%USERPROFILE%/.venvs/EU5Miner`.

## License

MIT. See [LICENSE](LICENSE).
