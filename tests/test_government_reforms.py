from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.government_reforms import parse_government_reform_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_common_government_reform_document(game_install: GameInstall) -> None:
    document = parse_government_reform_document(
        _read_text(game_install.representative_files()["government_reform_sample"])
    )

    definition = document.get_definition("religious_tolerance")
    assert definition is not None
    assert definition.age == "age_1_traditions"
    assert definition.societal_values == ("humanist_focus",)
    assert definition.country_modifier is not None
    assert definition.years == 2

    admiralty = document.get_definition("admiralty_regime_reform")
    assert admiralty is not None
    assert admiralty.major is True
    assert admiralty.potential is not None
    assert admiralty.allow is not None
    assert admiralty.on_activate is not None


@pytest.mark.timeout(5)
def test_parse_real_variant_government_reform_documents(game_install: GameInstall) -> None:
    monarchy = parse_government_reform_document(
        _read_text(game_install.representative_files()["government_reform_secondary_sample"])
    )
    special = parse_government_reform_document(
        _read_text(game_install.representative_files()["government_reform_special_sample"])
    )

    revolutionary_empire = monarchy.get_definition("revolutionary_empire")
    assert revolutionary_empire is not None
    assert revolutionary_empire.major is True
    assert revolutionary_empire.unique is True
    assert revolutionary_empire.government == "monarchy"
    assert revolutionary_empire.locked is not None
    assert revolutionary_empire.years == 1

    papacy = special.get_definition("papacy_reform")
    assert papacy is not None
    assert papacy.block_for_rebel is True
    assert papacy.location_modifier is not None
    assert papacy.on_activate is not None
    assert papacy.on_deactivate is not None
    assert "name_adrian" in papacy.male_regnal_names


def test_government_reform_parses_inline_variant_fields() -> None:
    document = parse_government_reform_document(
        "sample_reform = {\n"
        "    government = monarchy\n"
        "    major = yes\n"
        "    unique = no\n"
        "    block_for_rebel = yes\n"
        "    icon = sample_icon\n"
        "    societal_values = { value_a value_b }\n"
        "    male_regnal_names = { one two }\n"
        "    female_regnal_names = { three four }\n"
        "    potential = { always = yes }\n"
        "    allow = { always = yes }\n"
        "    locked = { always = no }\n"
        "    on_activate = { add = 1 }\n"
        "    on_fully_activated = { add = 2 }\n"
        "    on_deactivate = { add = 3 }\n"
        "    country_modifier = { tax = 1 }\n"
        "    province_modifier = { dev = 1 }\n"
        "    location_modifier = { attr = 1 }\n"
        "    years = 2\n"
        "    months = 3\n"
        "    weeks = 4\n"
        "    days = 5\n"
        "}\n"
    )

    definition = document.get_definition("sample_reform")
    assert definition is not None
    assert definition.government == "monarchy"
    assert definition.major is True
    assert definition.unique is False
    assert definition.block_for_rebel is True
    assert definition.icon == "sample_icon"
    assert definition.societal_values == ("value_a", "value_b")
    assert definition.male_regnal_names == ("one", "two")
    assert definition.female_regnal_names == ("three", "four")
    assert definition.potential is not None
    assert definition.allow is not None
    assert definition.locked is not None
    assert definition.on_activate is not None
    assert definition.on_fully_activated is not None
    assert definition.on_deactivate is not None
    assert definition.country_modifier is not None
    assert definition.province_modifier is not None
    assert definition.location_modifier is not None
    assert definition.years == 2
    assert definition.months == 3
    assert definition.weeks == 4
    assert definition.days == 5
