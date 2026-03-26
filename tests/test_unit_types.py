from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.unit_types import parse_unit_type_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_unit_type_document(game_install: GameInstall) -> None:
    document = parse_unit_type_document(
        _read_text(game_install.representative_files()["unit_type_sample"])
    )

    definition = document.get_definition("a_order_knights")
    assert definition is not None
    assert definition.is_special is True
    assert definition.category == "army_cavalry"
    assert definition.copy_from == "a_age_1_traditions_cavalry"
    assert definition.upgrades_to == "a_order_knights_2"
    assert definition.buildable is True
    assert len(definition.mercenaries_per_location) == 1
    assert definition.mercenaries_per_location[0].pop_type == "nobles"
    assert definition.mercenaries_per_location[0].multiply == "0.5"
    assert definition.gfx_tags == ("crusader_tag", "heavy_tag")
    assert definition.get_modifier("morale_damage_taken") == "-0.25"
    assert definition.combat is not None


@pytest.mark.timeout(5)
def test_parse_real_variant_unit_type_document(game_install: GameInstall) -> None:
    document = parse_unit_type_document(
        _read_text(game_install.representative_files()["unit_type_secondary_sample"])
    )

    definition = document.get_definition("a_discovery_conquistadors")
    assert definition is not None
    assert definition.is_special is True
    assert definition.category == "army_infantry"
    assert definition.copy_from == "a_age_3_discovery_infantry"
    assert definition.buildable is False
    assert definition.get_modifier("food_storage_per_strength") == "11"
    assert definition.gfx_tags == ("conquistador_tag", "cc", "heavy_tag")


def test_unit_type_parses_inline_variant_fields() -> None:
    document = parse_unit_type_document(
        "sample_unit = {\n"
        "    age = age_1\n"
        "    light = yes\n"
        "    default = no\n"
        "    use_ship_names = yes\n"
        "    assault = yes\n"
        "    bombard = no\n"
        "    auxiliary = yes\n"
        "    build_time = 30\n"
        "    build_time_modifier = 0.33\n"
        "    location_trigger = { coastal = yes }\n"
        "    location_potential = { can_recruit = yes }\n"
        "    country_potential = { exists = root }\n"
        "    limit = { value = 5 }\n"
        "    impact = { forest = -0.1 }\n"
        "    color = unit_green\n"
        "}\n"
    )

    definition = document.get_definition("sample_unit")
    assert definition is not None
    assert definition.age == "age_1"
    assert definition.light is True
    assert definition.default is False
    assert definition.use_ship_names is True
    assert definition.assault is True
    assert definition.bombard is False
    assert definition.auxiliary is True
    assert definition.build_time == "30"
    assert definition.build_time_modifier == "0.33"
    assert definition.location_trigger is not None
    assert definition.location_potential is not None
    assert definition.country_potential is not None
    assert isinstance(definition.limit, SemanticObject)
    assert definition.impact is not None
    assert definition.color == "unit_green"
