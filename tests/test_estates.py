from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.estates import parse_estate_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_estate_document(game_install: GameInstall) -> None:
    document = parse_estate_document(_read_text(game_install.representative_files()["estate_sample"]))

    crown = document.get_definition("crown_estate")
    assert crown is not None
    assert crown.color == "estate_crown"
    assert crown.power_per_pop == 0
    assert crown.tax_per_pop == 0
    assert crown.priority_for_dynasty_head is True
    assert crown.can_spawn_random_characters is False
    assert crown.high_power is not None
    assert crown.low_power is not None
    assert crown.power is not None
    assert crown.ruler is True

    nobles = document.get_definition("nobles_estate")
    assert nobles is not None
    assert nobles.color == "pop_nobles"
    assert nobles.power_per_pop == 25
    assert nobles.tax_per_pop == 100
    assert nobles.rival == pytest.approx(-0.01)
    assert nobles.alliance == pytest.approx(0.01)
    assert nobles.characters_have_dynasty == "always"
    assert nobles.can_generate_mercenary_leaders is True
    assert nobles.bank is True
    assert nobles.satisfaction is not None
    assert nobles.opinion is not None


def test_estate_parses_inline_variant_fields() -> None:
    document = parse_estate_document(
        "sample_estate = {\n"
        "    color = sample_color\n"
        "    power_per_pop = 7\n"
        "    tax_per_pop = 13\n"
        "    rival = -0.5\n"
        "    alliance = 0.25\n"
        "    revolt_court_language = court_language\n"
        "    priority_for_dynasty_head = yes\n"
        "    can_spawn_random_characters = no\n"
        "    characters_have_dynasty = always\n"
        "    can_generate_mercenary_leaders = yes\n"
        "    bank = no\n"
        "    ruler = yes\n"
        "    use_diminutive = no\n"
        "    satisfaction = { add = 1 }\n"
        "    high_power = { add = 2 }\n"
        "    low_power = { add = 3 }\n"
        "    power = { add = 4 }\n"
        "    opinion = { add = { value = 1 } }\n"
        "}\n"
    )

    definition = document.get_definition("sample_estate")
    assert definition is not None
    assert definition.color == "sample_color"
    assert definition.power_per_pop == 7
    assert definition.tax_per_pop == 13
    assert definition.rival == pytest.approx(-0.5)
    assert definition.alliance == pytest.approx(0.25)
    assert definition.revolt_court_language == "court_language"
    assert definition.priority_for_dynasty_head is True
    assert definition.can_spawn_random_characters is False
    assert definition.characters_have_dynasty == "always"
    assert definition.can_generate_mercenary_leaders is True
    assert definition.bank is False
    assert definition.ruler is True
    assert definition.use_diminutive is False
    assert definition.satisfaction is not None
    assert definition.high_power is not None
    assert definition.low_power is not None
    assert definition.power is not None
    assert definition.opinion is not None
