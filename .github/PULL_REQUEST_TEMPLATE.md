## Affected package
- [ ] Core (`eu5miner`)
- [ ] MCP (`eu5miner-mcp`)
- [ ] GUI (`eu5miner-gui`)
- [ ] Umbrella / docs / CI

## Summary
<!-- What changed and why -->

## Validation
- [ ] `uv sync --all-packages --extra=dev` clean
- [ ] `uv run pytest` passes for affected member(s)
- [ ] `uv run ruff check .` clean
- [ ] `uv run mypy packages/<affected>/src` clean
