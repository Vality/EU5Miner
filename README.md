# EU5Miner

A modular toolkit for working with Europa Universalis V game data, distributed as a single Python package with optional MCP server and Kivy desktop UI surfaces.

## Surfaces

- **`eu5miner`** — Core library and CLI. Pure-Python, no runtime deps beyond the stdlib. Entry point: `eu5miner`.
- **`eu5miner.mcp`** — Optional MCP server (installed via the `[mcp]` extra). Entry point: `eu5miner-mcp`.
- **`eu5miner.gui`** — Optional Kivy desktop UI (installed via the `[gui]` extra). Entry points: `eu5miner-gui`, `eu5miner-gui-shell`.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/) (optional but recommended for dev work).

```bash
# Core only (library + CLI)
pip install eu5miner

# Add MCP support
pip install eu5miner[mcp]

# Add GUI support
pip install eu5miner[gui]

# Everything
pip install eu5miner[all]
```

Without the matching extra, the corresponding submodule will raise an `ImportError` directing you to install the extra.

## Development

```bash
git clone https://github.com/Vality/EU5Miner.git
cd EU5Miner
uv sync --extra=dev
cd packages/core
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

A Windows setup script is provided at `scripts/setup-centralized-uv.ps1` for users who prefer a centralized venv under `%USERPROFILE%/.venvs/EU5Miner`.

## Migration from earlier releases

See [RENAMING.md](RENAMING.md). The `eu5miner-mcp` and `eu5miner-gui` Python distributions (≤ v0.7.x) are no longer published; their code now lives inside the unified `eu5miner` wheel.

## License

MIT. See [LICENSE](LICENSE).
