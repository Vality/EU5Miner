# EU5Miner

EU5Miner is a text-first Python library for reading, indexing, and planning edits to Europa Universalis V data and mod files.

Release `0.5.0` is the first public preview release.

The current release focuses on the major moddable text-based file families:

- Clausewitz-style script text used in `common`, `events`, `setup`, and `map_data`
- GUI script
- Localization YAML
- JSON metadata
- Semicolon-delimited CSV

The project is intentionally test-heavy. Core functionality is validated against representative real EU5 install files so later parser work is anchored in observed game behavior instead of assumptions.

## Status

The `0.5.x` line should be treated as a public preview.

- The root package, grouped domain packages, and the `eu5miner.mods` facade are intended for real use.
- The CLI is intended as a thin convenience surface over the same library APIs.
- Additional helper layers, future editing surfaces, and the planned MCP and GUI packages are still expected to evolve before `1.0`.

In practice, this release is suitable for install inspection, virtual filesystem queries, representative parsing, typed domain reads, and the current mod update planning and application workflow. It is not yet a promise that every exported helper will remain unchanged across future minor releases.

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
eu5miner list-systems
eu5miner list-files --phase in_game --subpath gui --limit 10
eu5miner analyze-script --representative scripted_trigger
eu5miner report-system --install-root C:\EU5 --system economy
eu5miner report-system --install-root C:\EU5 --system diplomacy
eu5miner plan-mod-update --install-root C:\EU5 --mod-root C:\mods\my_mod --phase in_game --subtree common/buildings --content-root C:\work\content
eu5miner apply-mod-update --install-root C:\EU5 --mod-root C:\mods\my_mod --phase in_game --subtree common/buildings --content-root C:\work\content
```

`list-systems` and `report-system` provide install-backed summaries for the major connected systems currently implemented in the library: `economy`, `diplomacy`, `government`, `religion`, `interface`, and `map`.

The mod workflow commands print a structured report to stdout, `note:` advisories for planned metadata actions such as `replace_path` additions, and `warning:` diagnostics for intended outputs that will still be shadowed by later sources.

## Library

The root package exposes install discovery, VFS primitives, and the public mod workflow facade:

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

Implemented domain adapters are re-exported from `eu5miner.domains` so callers do not need to import individual domain modules directly:

```python
from eu5miner.domains import (
	build_on_action_catalog_document,
	build_country_description_category_usage_document,
	parse_building_category_document,
	parse_building_type_document,
	parse_goods_demand_category_document,
	parse_goods_demand_document,
	parse_goods_document,
	parse_employment_system_document,
	parse_on_action_document,
	parse_on_action_documentation,
	parse_price_document,
	parse_production_method_document,
	parse_country_description_category_document,
	parse_culture_document,
	parse_religion_document,
	parse_scripted_list_document,
	parse_scripted_relation_document,
	parse_scripted_modifier_document,
	parse_script_value_document,
	parse_scripted_trigger_document,
	parse_setup_country_document,
)

on_action_document = parse_on_action_document("on_example = { events = { flavor_test.1 } }\n")
on_action_docs = parse_on_action_documentation(
	"On Action Documentation:\n\n"
	"--------------------\n\n"
	"on_example:\n"
	"From Code: Yes\n"
	"Expected Scope: country\n"
)
building_category_document = parse_building_category_document("trade_category = {}\n")
building_type_document = parse_building_type_document(
	"granary = { category = infrastructure_category pop_type = peasants }\n"
)
goods_document = parse_goods_document("iron = { method = mining category = raw_material }\n")
goods_demand_category_document = parse_goods_demand_category_document(
	"building_construction = { display = integer }\n"
)
goods_demand_document = parse_goods_demand_document(
	"sample_demand = { iron = 0.5 category = special_demands }\n"
)
production_method_document = parse_production_method_document(
	"maintenance = { tools = 0.1 category = building_maintenance }\n"
)
price_document = parse_price_document("build_road = { gold = 10 }\n")
employment_system_document = parse_employment_system_document(
	"equality = { priority = { value = 1 } }\n"
)
category_document = parse_country_description_category_document("military = {}\n")
culture_document = parse_culture_document("example_culture = { culture_groups = { group_a } }\n")
religion_document = parse_religion_document("example_faith = { group = abrahamic }\n")
list_document = parse_scripted_list_document("adult = { base = character conditions = { is_adult = yes } }\n")
relation_document = parse_scripted_relation_document("my_relation = { type = diplomacy relation_type = mutual }\n")
modifier_document = parse_scripted_modifier_document("my_modifier = { modifier = { add = 1 } }\n")
script_value_document = parse_script_value_document("minor_stress_gain = 10\n")
trigger_document = parse_scripted_trigger_document("test_trigger = { always = yes }\n")
country_document = parse_setup_country_document("FRA = { tier = kingdom }\n")

on_action_catalog = build_on_action_catalog_document([on_action_document], on_action_docs)

category_usage = build_country_description_category_usage_document(
	category_document,
	country_document,
)
```

For mod update workflows in the preview release, `eu5miner.mods` remains the stable higher-level seam, while the CLI stays a thin wrapper over the same plan/apply/report operations.

Grouped domain packages are the preferred stable seam when you want to stay inside one concept area instead of importing from the fully curated top-level surface. For grouped families, prefer package-level imports such as `eu5miner.domains.diplomacy` over internal implementation modules like `eu5miner.domains.diplomacy.casus_belli`:

```python
from eu5miner.domains.diplomacy import (
	build_diplomacy_graph_catalog,
	parse_casus_belli_document,
	parse_wargoal_document,
)
from eu5miner.domains.economy import build_market_catalog, parse_goods_document, parse_price_document
from eu5miner.domains.government import build_government_catalog, parse_government_type_document
from eu5miner.domains.localization import build_localization_bundle
from eu5miner.domains.map import build_linked_location_document, parse_default_map_document
from eu5miner.domains.religion import build_religion_catalog, parse_religion_document
from eu5miner.domains.units import parse_unit_type_document
```

## Testing

The suite includes timeout protection for parser-sensitive tests so future performance regressions fail quickly instead of appearing to hang indefinitely.

## Configuration

The test suite and install-discovery helpers use this precedence for the game install path:

1. `EU5_INSTALL_DIR`
2. The default Steam install path on Windows

## Documentation

The planning entrypoint is [ROADMAP.md](ROADMAP.md).

Execution-ready work packages for contributors and cloud agents live in [documents/specs/README.md](documents/specs/README.md).

Architecture constraints and layering rules live in [documents/architecture.md](documents/architecture.md).

Developer environment notes for the OneDrive/`uv` workflow live in [documents/development-environment.md](documents/development-environment.md).

Historical planning notes remain in older files under `documents/`, but roadmap and spec work should start from the roadmap/spec split rather than the legacy plan documents.

Release history is tracked in [CHANGELOG.md](CHANGELOG.md).
