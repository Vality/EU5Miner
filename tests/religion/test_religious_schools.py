from __future__ import annotations

from pathlib import Path

from eu5miner.domains.religion.religious_schools import parse_religious_school_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_real_religious_school_documents(game_install: GameInstall) -> None:
    sunni = parse_religious_school_document(
        _read_text(game_install.representative_files()["religious_school_sample"])
    )
    hindu = parse_religious_school_document(
        _read_text(game_install.representative_files()["religious_school_secondary_sample"])
    )

    hanafi = sunni.get_definition("hanafi_school")
    assert hanafi is not None
    assert hanafi.color == "rgb"
    assert hanafi.enabled_for_country is not None
    assert hanafi.enabled_for_character is not None
    assert hanafi.modifier is not None

    yoga = hindu.get_definition("yoga_school")
    assert yoga is not None
    assert yoga.modifier is not None
    assert yoga.modifier.get_scalar("global_population_growth") == "0.00025"


def test_religious_school_parses_inline_fields() -> None:
    document = parse_religious_school_document(
        "sample_school = {\n"
        "    color = rgb { 1 2 3 }\n"
        "    enabled_for_country = { always = yes }\n"
        "    enabled_for_character = { religion = religion:catholic }\n"
        "    modifier = { tolerance_own = 1 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_school")
    assert definition is not None
    assert definition.color == "rgb"
    assert definition.enabled_for_country is not None
    assert definition.enabled_for_character is not None
    assert definition.modifier is not None
