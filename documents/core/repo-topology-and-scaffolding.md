# Repo topology and scaffolding

EU5Miner is published as a single Python distribution, `eu5miner`, with the MCP server and Kivy desktop UI as optional submodules under `eu5miner.mcp` and `eu5miner.gui`.

```
EU5Miner/
├── pyproject.toml             # umbrella project (optional extras: [mcp], [gui], [all])
├── uv.lock                    # single root lockfile
├── packages/
│   └── core/                  # single Python distribution: eu5miner
│       ├── pyproject.toml
│       ├── src/
│       │   ├── eu5miner/      # core library + CLI
│       │   ├── eu5miner/mcp/  # optional MCP server ([mcp] extra)
│       │   └── eu5miner/gui/  # optional Kivy UI ([gui] extra)
│       └── tests/
├── documents/                 # umbrella-level design docs
├── .github/                   # CI, issue templates, dependabot
├── scripts/                   # dev setup helpers
└── README.md
```

## Conventions

- The whole distribution uses Python 3.12, the hatchling build backend, pytest, ruff, and mypy strict.
- `packages/core/pyproject.toml` holds the `[project]` metadata and declares the optional extras.
- The root `pyproject.toml` is the umbrella-level project; there is no `[tool.uv.workspace]` block.
- The MCP and GUI submodules live inside the same wheel as optional surfaces. They are not separate distributions.
- Cross-module imports go by name (`from eu5miner import ...`, `from eu5miner.mcp import ...`, `from eu5miner.gui import ...`). Never use `..` relative imports across the core library and its submodules.
- Optional surfaces gate at import time: importing `eu5miner.mcp` without the `[mcp]` extra installed raises `ImportError`.
