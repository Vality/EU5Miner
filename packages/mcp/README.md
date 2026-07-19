# EU5Miner MCP server (`eu5miner-mcp`)

Part of the [EU5Miner workspace](https://github.com/Vality/EU5Miner). See the umbrella [README.md](../../README.md) for install and layout. This package is also installable as `pip install eu5miner-mcp` or as an extra on core: `pip install eu5miner[mcp]`.

EU5Miner-mcp is an unofficial MCP application for exposing selected `eu5miner` capabilities through a thin server surface for Europa Universalis V installs and mods.

EU5Miner-mcp is not affiliated with Paradox Interactive or the Europa Universalis franchise.

No game files, extracted assets, or other proprietary game content are included in this package. The tool surface is intended to inspect a user's own local install and mod directories.

The current surface is intentionally narrow: the shipped MCP tools wrap stable `eu5miner` inspection, VFS, entity-browsing, grouped helper, and mod workflow seams without duplicating parser or domain logic.

## Status

- The current `0.7.x` line should be treated as a public preview rather than a stable `1.0` API.
- The implementation is a typed MCP server shell over stable `eu5miner` inspection, VFS, entity-browsing, grouped helper, and mod workflow seams.
- The active registered tools are `inspect-install`, `list-files`, `list-systems`, `report-system`, `list-entity-systems`, `find-entity`, `describe-entity`, `list-entity-links`, `report-diplomacy-war-flow`, `report-diplomacy-graph`, `report-religion-links`, `plan-mod-update`, `apply-mod-update`, and `describe-server`.
- The CLI can still print the startup status line, describe the registered tools with `--describe`, and serve the same registry over real stdio MCP transport with `--stdio`.
- MCP clients can call `describe-server` to retrieve display, server, and package names, version, available transports, tool names and counts, write-tool names and counts, stdio instructions, and the live registered tool descriptors from the same shared registry the CLI and stdio transport use.
- The registry-backed runtime layer fails fast if duplicate tool names, missing configured write tools, or mismatched `describe-server` descriptor ordering would otherwise publish inconsistent contract metadata.
- The grouped-helper seam includes shipped diplomacy war-flow, diplomacy-graph, and religion link reports over representative install files only.
- Parsing, VFS, and domain logic should continue to live in the core `eu5miner` library.

The checked-in package is aligned to the coordinated `eu5miner` umbrella release line rather than a moving mainline revision.

## Current Shell Behavior

The preview shell currently exposes a narrow tool registry:

- `describe-server`: describe the runtime metadata, transports, tool and write-tool counts, stdio instructions, confirmation requirements, and current registered MCP tool descriptors
- `inspect-install`: summarize discovered install roots and ordered content sources
- `list-files`: list merged visible files for one content phase and optional subpath
- `list-systems`: list the stable system reports exposed by the core inspection facade
- `report-system`: build a higher-level report for one supported system
- `list-entity-systems`: list the narrow browseable entity systems and their primary entity kinds
- `find-entity`: browse one supported entity system with an optional case-insensitive name filter
- `describe-entity`: return the summary, fields, and linked references for one named entity
- `list-entity-links`: return only the linked references for one named entity
- `report-diplomacy-war-flow`: build the core diplomacy war-flow helper report from representative install files
- `report-diplomacy-graph`: build the core diplomacy graph helper report from representative install files
- `report-religion-links`: build the core religion link helper report from representative install files
- `plan-mod-update`: plan a mod update and return both the formatted report and structured write metadata without applying changes
- `apply-mod-update`: apply a mod update and return both the formatted report and structured materialization result; requires `confirm=true` because it writes files under the target mod root

The entity-browsing slice is intentionally narrow. It wraps the core `eu5miner.inspection` browseable subset instead of inventing a generic graph API in the MCP layer, so the current real entity tools cover `economy` goods, `diplomacy` casus belli, `government` government types, `religion` religions, and `map` locations. For diplomacy, `describe-entity` and `list-entity-links` surface the same linked wargoal, peace-treaty, and country-interaction references already curated by the core inspection seam. The `list-entity-links` tool is only a convenience view over the same core reference list already returned by `describe-entity`; it does not introduce separate graph traversal behavior in the MCP layer.

The grouped-helper expansion stays similarly constrained. `report-diplomacy-war-flow`, `report-diplomacy-graph`, and `report-religion-links` read the representative install files already curated by `GameInstall.representative_files()`, then delegate report building to the stable grouped `eu5miner.domains.diplomacy` and `eu5miner.domains.religion` helper APIs. The MCP layer only shapes the tool contracts and serialization.

The mod workflow is also intentionally conservative at the MCP boundary: `plan-mod-update` remains the dry-run entrypoint, `apply-mod-update` requires an explicit `confirm=true` argument so hosted or interactive clients do not trigger writes accidentally, and `describe-server` exposes that same write-confirmation boundary together with the stdio startup instructions and active tool-name registry in a machine-readable form.

At this stage the package is best understood as a thin typed MCP-facing server and CLI entrypoint over a narrow inspection, entity-browsing, grouped-helper, runtime-description, and mod workflow surface, not as a broad production MCP integration.

## Development

From the umbrella root:

```bash
git clone https://github.com/Vality/EU5Miner.git
cd EU5Miner
uv sync --all-packages --extra=dev
cd packages/mcp
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

The Windows setup script at `scripts/setup-centralized-uv.ps1` keeps the centralized `uv` environment usable under OneDrive.

## CLI

The package currently ships a thin preview CLI:

```powershell
eu5miner-mcp
eu5miner-mcp --describe
eu5miner-mcp --stdio
```

## Documentation

- Umbrella planning entrypoint: [ROADMAP.md](../../ROADMAP.md)
- Umbrella release history: [CHANGELOG.md](../../CHANGELOG.md)
- MCP package execution-ready specs: [documents/specs/README.md](documents/specs/README.md)
- Architecture notes: [documents/architecture.md](documents/architecture.md)
- Environment notes: [documents/development-environment.md](documents/development-environment.md)
