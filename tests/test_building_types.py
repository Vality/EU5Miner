from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.building_types import parse_building_type_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_building_type_document(game_install: GameInstall) -> None:
    document = parse_building_type_document(
        _read_text(game_install.representative_files()["building_type_sample"])
    )

    assert len(document.definitions) >= 5

    irrigation = document.get_definition("irrigation_systems")
    assert irrigation is not None
    assert irrigation.category == "infrastructure_category"
    assert irrigation.pop_type == "peasants"
    assert irrigation.max_levels == "irrigant_cap"
    assert irrigation.is_foreign is False
    assert irrigation.location_ranks == ("rural_settlement", "town", "city")
    assert irrigation.location_potential is not None
    assert irrigation.unique_production_methods is not None
    assert irrigation.construction_demand == "village_construction"
    assert irrigation.modifier is not None

    bridge = document.get_definition("bridge_infrastructure")
    assert bridge is not None
    assert bridge.allow is not None
    assert bridge.possible_production_methods == (("bridge_maintenance",),)


@pytest.mark.timeout(5)
def test_parse_secondary_real_building_type_document(game_install: GameInstall) -> None:
    document = parse_building_type_document(
        _read_text(game_install.representative_files()["building_type_secondary_sample"])
    )

    definition = document.get_definition("royal_court")
    assert definition is not None
    assert definition.category == "government_category"
    assert definition.expensive is True
    assert definition.location_potential is not None
    assert definition.country_potential is not None
    assert definition.remove_if is not None
    assert definition.capital_country_modifier is not None
    assert definition.graphical_tags == ("palace",)


def test_building_type_parses_inline_fields_and_parameters() -> None:
    document = parse_building_type_document(
        "test_building = {\n"
        "    is_foreign = yes\n"
        "    pop_type = laborers\n"
        "    category = defense_category\n"
        "    max_levels = $CAP$\n"
        "    rural_settlement = yes\n"
        "    town = yes\n"
        "    possible_production_methods = { maintenance_a maintenance_b }\n"
        "    custom_tags = { one two }\n"
        "    allow = { exists = $TARGET$ }\n"
        "    modifier = { local_unrest = -0.1 }\n"
        "}\n"
    )

    definition = document.get_definition("test_building")
    assert definition is not None
    assert definition.is_foreign is True
    assert definition.pop_type == "laborers"
    assert definition.category == "defense_category"
    assert definition.max_levels == "$CAP$"
    assert definition.location_ranks == ("rural_settlement", "town")
    assert definition.possible_production_methods == (("maintenance_a", "maintenance_b"),)
    assert definition.custom_tags == ("one", "two")
    assert definition.allow is not None
    assert definition.modifier is not None
    assert definition.parameters == ("CAP", "TARGET")
