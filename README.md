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
eu5miner plan-mod-update --install-root C:\EU5 --mod-root C:\mods\my_mod --phase in_game --subtree common/buildings --content-root C:\work\content
eu5miner apply-mod-update --install-root C:\EU5 --mod-root C:\mods\my_mod --phase in_game --subtree common/buildings --content-root C:\work\content
```

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
	parse_on_action_document,
	parse_on_action_documentation,
	parse_price_document,
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
price_document = parse_price_document("build_road = { gold = 10 }\n")
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

For mod editing workflows, `eu5miner.mods` remains the stable higher-level seam, while the CLI stays a thin wrapper over the same plan/apply/report operations.

## Testing

The suite includes timeout protection for parser-sensitive tests so future performance regressions fail quickly instead of appearing to hang indefinitely.

## Configuration

The test suite and install-discovery helpers use this precedence for the game install path:

1. `EU5_INSTALL_DIR`
2. The default Steam install path on Windows

## Documentation

Design and research notes are stored in [documents/specification.md](documents/specification.md) and the other files in `documents/`.

Agent-facing resume and steering notes are in [AGENTS.md](AGENTS.md) and [documents/agent-resume-guide.md](documents/agent-resume-guide.md).

Developer environment notes for the OneDrive/`uv` workflow are in [documents/development-environment.md](documents/development-environment.md).

The planned game-data implementation order is tracked in [documents/data-type-roadmap.md](documents/data-type-roadmap.md).
