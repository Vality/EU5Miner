# Repo topology and scaffolding

EU5Miner is a uv workspace with three coordinated Python packages:

```
EU5Miner/
├── pyproject.toml             # workspace-only (no [project])
├── uv.lock                    # single root lockfile
├── packages/
│   ├── core/                  # eu5miner library + CLI
│   │   ├── pyproject.toml
│   │   ├── src/eu5miner/
│   │   └── tests/
│   ├── mcp/                   # eu5miner-mcp MCP server
│   │   ├── pyproject.toml
│   │   ├── src/eu5miner_mcp/
│   │   └── tests/
│   └── gui/                   # eu5miner-gui Kivy desktop UI
│       ├── pyproject.toml
│       ├── src/eu5miner_gui/
│       └── tests/
├── documents/                 # umbrella-level design docs
├── .github/                   # CI, issue templates, dependabot
├── scripts/                   # dev setup helpers
└── README.md
```

## Conventions

- All three packages share the same Python version (3.12), build backend (hatchling), test framework (pytest), linter (ruff), and type checker (mypy strict).
- Per-package `pyproject.toml` holds `[project]` metadata; the root `pyproject.toml` holds the workspace.
- Versions bump in lockstep: v0.7.0 across all three.
- Cross-package imports go by name (`from eu5miner import ...`). Never use `..` relative imports across packages.
- The MCP and GUI packages each declare `eu5miner >=0.7,<0.8` in their `[project].dependencies`. uv workspace resolves this to the local `packages/core/` member during development.