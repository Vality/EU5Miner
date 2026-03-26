from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.government.government_types import parse_government_type_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_government_type_document(game_install: GameInstall) -> None:
    document = parse_government_type_document(
        _read_text(game_install.representative_files()["government_type_sample"])
    )

    monarchy = document.get_definition("monarchy")
    assert monarchy is not None
    assert monarchy.use_regnal_number is True
    assert monarchy.government_power == "legitimacy"
    assert monarchy.revolutionary_country_antagonism == 20
    assert monarchy.default_character_estate == "nobles_estate"
    assert "cognatic_primogeniture" in monarchy.heir_selections
    assert monarchy.modifier is not None

    tribe = document.get_definition("tribe")
    assert tribe is not None
    assert tribe.generate_consorts is True
    assert tribe.map_color == "gov_tribe"
    assert tribe.government_power == "tribal_cohesion"


def test_government_type_parses_inline_variant_fields() -> None:
    document = parse_government_type_document(
        "sample_gov = {\n"
        "    use_regnal_number = no\n"
        "    generate_consorts = yes\n"
        "    heir_selection = elective\n"
        "    heir_selection = lottery\n"
        "    map_color = gov_sample\n"
        "    government_power = authority\n"
        "    revolutionary_country_antagonism = 7\n"
        "    default_character_estate = nobles_estate\n"
        "    modifier = { add = 1 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_gov")
    assert definition is not None
    assert definition.use_regnal_number is False
    assert definition.generate_consorts is True
    assert definition.heir_selections == ("elective", "lottery")
    assert definition.map_color == "gov_sample"
    assert definition.government_power == "authority"
    assert definition.revolutionary_country_antagonism == 7
    assert definition.default_character_estate == "nobles_estate"
    assert definition.modifier is not None
