# EU5Miner

EU5Miner is a text-first Python library for reading, indexing, and planning edits to Europa Universalis V data and mod files.

This is an unofficial community project. It is not affiliated with, endorsed by, or sponsored by Paradox Interactive or the Europa Universalis V development team.

The repository and published package do not include game assets. Real-file validation and many install-backed workflows expect a locally available EU5 installation.

Release `0.6.0` is the current public preview release.

The current release focuses on the major moddable text-based file families:

- Clausewitz-style script text used in `common`, `events`, `setup`, and `map_data`
- GUI script
- Localization YAML
- JSON metadata
- Semicolon-delimited CSV

The project is intentionally test-heavy. Core functionality is validated against representative real EU5 install files so later parser work is anchored in observed game behavior instead of assumptions.

## Status

The `0.6.x` line should be treated as a public preview.

Compared with `0.5.0`, this preview expands the stable read-only inspection seam with initial entity browsing for economy, diplomacy, government, religion, and map while keeping the public API deliberately curated.

- The root package, grouped domain packages, `eu5miner.inspection`, and the `eu5miner.mods` facade are intended for real use.
- The CLI is intended as a thin convenience surface over the same library APIs.
- Additional helper layers, future editing surfaces, and the downstream GUI and MCP packages are still expected to evolve before `1.0`.
- API coverage is intentionally incomplete relative to the full game data surface; missing families and API adjustments should still be expected during the preview line.

In practice, this release is suitable for install inspection, virtual filesystem queries, representative parsing, typed domain reads, and the current mod update planning and application workflow. It is not yet a promise that every exported helper will remain unchanged across future minor releases.

The recent stabilization rounds already locked the main preview contract around the narrow root package, grouped domain packages, `eu5miner.inspection`, `eu5miner.mods`, and the documented thin CLI workflow. That close-out work is now reflected in the checked-in docs and tests: the public-API and grouped-package contract tests, inspection contract coverage, thin CLI contract coverage, README contract examples, and the default no-install validation gate all point at the same boundary. A later `1.0` proposal should treat the remaining work as release execution plus targeted manual sanity checks against a local install and representative mod workspace, not as another feature phase.

That checked-in core state now also has matching downstream breadth in the companion preview repos: `EU5MinerGUI` and `EU5MinerMCP` both ship thin grouped-helper surfaces through diplomacy and religion, and those helper families remain the explicit preview boundary. The next cross-repo phase should focus on post-release validation, contract monitoring, and targeted manual sanity checks rather than widening helper scope again.

## Development

This repository is stored under OneDrive, so the recommended setup is to keep the `uv` environment outside the synced tree.

Initialize or refresh the centralized environment with:

```powershell
.\scripts\setup-centralized-uv.ps1
```

That script points `UV_PROJECT_ENVIRONMENT` at `%USERPROFILE%\.venvs\EU5Miner`, sets `UV_LINK_MODE=copy` for OneDrive-safe `uv` operations, and runs `uv sync --extra dev` there.

If you need a one-off local setup instead, install development dependencies with `uv`:

```powershell
uv sync --extra dev
```

Run the required baseline validation:

```powershell
$env:UV_PROJECT_ENVIRONMENT = "$env:USERPROFILE\.venvs\EU5Miner"
$env:UV_LINK_MODE = "copy"
uv run pytest
uv run ruff check .
uv run mypy src
uv build
```

Run the broader optional sweep explicitly when you want wider install-backed coverage:

```powershell
uv run python -m pytest -m broad
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
eu5miner list-systems
eu5miner list-files --phase in_game --subpath gui --limit 10
eu5miner analyze-script --representative scripted_trigger
eu5miner report-system --install-root C:\EU5 --system economy
eu5miner report-system --install-root C:\EU5 --system diplomacy
eu5miner plan-mod-update --install-root C:\EU5 --mod-root C:\mods\my_mod --phase in_game --subtree common/buildings --content-root C:\work\content
eu5miner apply-mod-update --install-root C:\EU5 --mod-root C:\mods\my_mod --phase in_game --subtree common/buildings --content-root C:\work\content
```

For the stabilization pass, treat these seven commands and their documented arguments as the intended thin CLI contract. Higher-level automation should prefer the library facades in `eu5miner.inspection` and `eu5miner.mods` rather than depending on internal CLI helpers.

Post-release stabilization work should keep that command list stable unless a concrete compatibility problem is found. It is not an invitation to widen the CLI before `1.0`.

`list-systems` and `report-system` provide install-backed summaries for the major connected systems currently implemented in the library: `economy`, `diplomacy`, `government`, `religion`, `interface`, and `map`.

The mod workflow commands print a structured report to stdout, `note:` advisories for planned metadata actions such as `replace_path` additions, and `warning:` diagnostics for intended outputs that will still be shadowed by later sources.

## Library

The root package intentionally stays narrow. It exposes install discovery, VFS primitives, and the public mod workflow facade:

```python
from pathlib import Path

from eu5miner import ContentPhase, GameInstall, VirtualFilesystem, plan_mod_update

install = GameInstall.discover(r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V")
vfs = VirtualFilesystem.from_install(install)

merged = vfs.get_merged_file(ContentPhase.IN_GAME, Path("gui") / "agenda_view.gui")
assert merged is not None

update = plan_mod_update(
	vfs,
	"my_mod",
	ContentPhase.IN_GAME,
	Path("common") / "buildings",
	intended_relative_paths=(Path("common") / "buildings" / "a.txt",),
	content_by_relative_path={Path("common") / "buildings" / "a.txt": "building = {}\n"},
)
```

The root package does not also re-export install inspection helpers or domain parsing helpers. Keep those imports explicit so downstream code can depend on the intended stable seams.

For downstream GUI and MCP consumers that need a stable read-only seam for install discovery, high-level system summaries, and initial entity browsing, use `eu5miner.inspection` instead of reaching into CLI helpers:

```python
from eu5miner import GameInstall
from eu5miner.inspection import (
	get_system_entity,
	format_install_summary,
	format_system_report,
	get_system_report,
	inspect_install,
	list_entity_systems,
	list_system_entities,
	list_supported_systems,
)

summary = inspect_install(r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V")
print(format_install_summary(summary))

systems = list_supported_systems()
economy_report = get_system_report(
	GameInstall.discover(summary.root),
	"economy",
)
print(format_system_report(economy_report))

entity_systems = list_entity_systems()
economy_entities = list_system_entities(
	GameInstall.discover(summary.root),
	"economy",
)
iron = get_system_entity(
	GameInstall.discover(summary.root),
	"economy",
	"iron",
)
```

This inspection facade is the stable public entrypoint for install summaries, available system listing, install-backed system report retrieval, and a deliberately narrow entity-browsing seam. The current browseable subset is intentionally limited to one primary entity family per system: `economy` goods, `diplomacy` casus belli, `government` government types, `religion` religions, and `map` linked locations. That keeps the preview API useful for GUI and MCP read-only flows without overcommitting to a generic graph API across every catalog family yet. The CLI remains a thin wrapper over the same library surface.

For domain adapters and higher-level helpers, prefer grouped package entrypoints when you are working within one concept area. They are the clearest stable seam for downstream library consumers:

```python
from eu5miner.domains.diplomacy import (
	build_diplomacy_graph_catalog,
	build_war_flow_catalog,
	parse_casus_belli_document,
	parse_country_interaction_document,
	parse_peace_treaty_document,
	parse_subject_type_document,
	parse_wargoal_document,
)
from eu5miner.domains.economy import (
	build_market_catalog,
	parse_goods_document,
	parse_price_document,
)
from eu5miner.domains.government import build_government_catalog, parse_government_type_document
from eu5miner.domains.localization import build_localization_bundle
from eu5miner.domains.map import build_linked_location_document, parse_default_map_document
from eu5miner.domains.religion import build_religion_catalog, parse_religion_document
from eu5miner.domains.units import parse_unit_category_document

casus_belli_document = parse_casus_belli_document(
	"sample_cb = { war_goal_type = superiority }\n"
)
wargoal_document = parse_wargoal_document(
	"superiority = { type = superiority attacker = { conquer_cost = 1 } }\n"
)
peace_treaty_document = parse_peace_treaty_document(
	"peace_example = { effect = { make_subject_of = { type = subject_type:sample_subject } } }\n"
)
subject_type_document = parse_subject_type_document(
	"sample_subject = { level = 1 allow_subjects = no }\n"
)
country_interaction_document = parse_country_interaction_document(
	"sample_country_interaction = { type = diplomacy }\n"
)

war_catalog = build_war_flow_catalog(
	casus_belli_documents=(casus_belli_document,),
	wargoal_documents=(wargoal_document,),
	peace_treaty_documents=(peace_treaty_document,),
	subject_type_documents=(subject_type_document,),
)
diplomacy_catalog = build_diplomacy_graph_catalog(
	casus_belli_documents=(casus_belli_document,),
	wargoal_documents=(wargoal_document,),
	peace_treaty_documents=(peace_treaty_document,),
	subject_type_documents=(subject_type_document,),
	country_interaction_documents=(country_interaction_document,),
)

goods_document = parse_goods_document("iron = { method = mining category = raw_material }\n")
price_document = parse_price_document("build_road = { gold = 10 }\n")
market_catalog = build_market_catalog(
	goods_documents=(goods_document,),
	price_documents=(price_document,),
)

government_type_document = parse_government_type_document(
	"monarchy = { heir_selection = cognatic government_power = legitimacy }\n"
)
government_catalog = build_government_catalog(
	government_type_documents=(government_type_document,),
)

religion_document = parse_religion_document("example_faith = { group = abrahamic }\n")
religion_catalog = build_religion_catalog(religion_documents=(religion_document,))

default_map_document = parse_default_map_document('setup = "definitions.txt"\n')
localization_bundle = build_localization_bundle(
	(("sample.yml", 'l_english:\nSAMPLE_KEY: "Sample"\n'),)
)
unit_category_document = parse_unit_category_document(
	"sample_category = { is_army = yes startup_amount = 1 }\n"
)
```

For mod update workflows in the preview release, `eu5miner.mods` remains the stable higher-level seam, while the CLI stays a thin wrapper over the same plan/apply/report operations.

The broad `eu5miner.domains` convenience export remains available for callers that genuinely want one import hub across many domains, but grouped packages are the preferred stable seam when the concept area is clear. Avoid reaching into internal implementation modules such as `eu5miner.domains.diplomacy.casus_belli` or `eu5miner.domains.map.map_text` from downstream code.

## Testing

The default baseline keeps `uv run pytest` warning-free even when plugin-specific pytest options are unavailable.

When the development environment includes `pytest-timeout` via `uv sync --extra dev`, the suite also applies a global per-test timeout and preserves the per-test `@pytest.mark.timeout(...)` overrides used by parser-sensitive tests.

## Configuration

The test suite and install-discovery helpers use this precedence for the game install path:

1. `EU5_INSTALL_DIR`
2. The default Steam install path on Windows

## Documentation

The planning entrypoint is [ROADMAP.md](ROADMAP.md).

For the current `1.0` boundary and blocker set, use [documents/v1-scope.md](documents/v1-scope.md) together with [documents/v1-release-readiness.md](documents/v1-release-readiness.md).

Execution-ready work packages for contributors and cloud agents live in [documents/specs/README.md](documents/specs/README.md).

Architecture constraints and layering rules live in [documents/architecture.md](documents/architecture.md).

Developer environment notes for the OneDrive/`uv` workflow live in [documents/development-environment.md](documents/development-environment.md).

Historical planning notes remain in older files under `documents/`, but roadmap and spec work should start from the roadmap/spec split rather than the legacy plan documents.

Release history is tracked in [CHANGELOG.md](CHANGELOG.md).
