from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.map.setup_countries import parse_setup_country_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_setup_country_document(game_install: GameInstall) -> None:
    document = parse_setup_country_document(
        _read_text(game_install.representative_files()["setup_country_sample"])
    )

    assert len(document.definitions) > 10
    assert document.definitions[0].tag == "BRI"

    france = document.get_definition("FRA")
    assert france is not None
    assert france.culture_definition == "french"
    assert france.religion_definition == "catholic"
    assert france.description_category == "military"
    assert france.difficulty == 3


def test_parse_setup_country_inline_definition() -> None:
    document = parse_setup_country_document(
        "FRA = {\n"
        "    color = map_FRA\n"
        "    color2 = rgb { 16 41 202 }\n"
        "    culture_definition = french\n"
        "    religion_definition = catholic\n"
        "    description_category = military\n"
        "    difficulty = 3\n"
        "}\n"
    )

    france = document.get_definition("FRA")
    assert france is not None
    assert france.color == "map_FRA"
    assert france.color2 == "rgb"
    assert france.get_scalar("religion_definition") == "catholic"
    assert france.difficulty == 3


def test_parse_setup_country_schema_sample() -> None:
    document = parse_setup_country_document(
        "TAG = {\n"
        "    color = hsv360 { 360 100 100 }\n"
        "    color2 = hsv360 { 0 0 0 }\n"
        "    description_category = administrative\n"
        "    difficulty = 2\n"
        "}\n"
    )

    definition = document.get_definition("TAG")
    assert definition is not None
    assert definition.color == "hsv360"
    assert definition.color2 == "hsv360"
    assert definition.description_category == "administrative"
    assert definition.difficulty == 2

