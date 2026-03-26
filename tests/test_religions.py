from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.religions import parse_religion_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_religion_document(game_install: GameInstall) -> None:
    document = parse_religion_document(
        _read_text(game_install.representative_files()["religion_sample"])
    )

    assert len(document.definitions) > 5

    definition = document.get_definition("catholic")
    assert definition is not None
    assert definition.group == "christian"
    assert definition.color == "religion_catholic"
    assert definition.language == "latin_language"
    assert definition.needs_reform is True
    assert definition.has_religious_head is True
    assert definition.has_cardinals is True
    assert definition.important_country == "PAP"
    assert definition.tithe == 0.02
    assert "catholic_gfx" in definition.tags
    assert any(opinion.religion == "orthodox" for opinion in definition.opinions)


@pytest.mark.timeout(5)
def test_parse_secondary_real_religion_document(game_install: GameInstall) -> None:
    document = parse_religion_document(
        _read_text(game_install.representative_files()["religion_secondary_sample"])
    )

    definition = document.get_definition("shinto")
    assert definition is not None
    assert definition.group == "buddhist"
    assert definition.has_purity is True
    assert definition.has_honor is True
    assert definition.max_sects == 1
    assert "imperial_court" in definition.factions


def test_religion_document_parses_lists_flags_and_opinions() -> None:
    document = parse_religion_document(
        "example_faith = {\n"
        "    color = color_example\n"
        "    group = example_group\n"
        "    language = example_language\n"
        "    enable = 1200.1.1\n"
        "    tithe = 0.05\n"
        "    religious_aspects = 3\n"
        "    max_sects = 2\n"
        "    ai_wants_convert = yes\n"
        "    has_religious_influence = yes\n"
        "    religious_school = school_a\n"
        "    religious_school = school_b\n"
        "    religious_focuses = { focus_a focus_b }\n"
        "    num_religious_focuses_needed_for_reform = 2\n"
        "    tags = { gfx_a gfx_b }\n"
        "    custom_tags = { tag_a tag_b }\n"
        "    unique_names = { name_one name_two }\n"
        "    factions = { faction_a faction_b }\n"
        "    opinions = {\n"
        "        other = positive\n"
        "        rival = enemy\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("example_faith")
    assert definition is not None
    assert definition.color == "color_example"
    assert definition.group == "example_group"
    assert definition.language == "example_language"
    assert definition.enable == "1200.1.1"
    assert definition.tithe == 0.05
    assert definition.religious_aspects == 3
    assert definition.max_sects == 2
    assert definition.ai_wants_convert is True
    assert definition.has_religious_influence is True
    assert definition.religious_schools == ("school_a", "school_b")
    assert definition.religious_focuses == ("focus_a", "focus_b")
    assert definition.num_religious_focuses_needed_for_reform == 2
    assert definition.tags == ("gfx_a", "gfx_b")
    assert definition.custom_tags == ("tag_a", "tag_b")
    assert definition.unique_names == ("name_one", "name_two")
    assert definition.factions == ("faction_a", "faction_b")
    assert [(opinion.religion, opinion.stance) for opinion in definition.opinions] == [
        ("other", "positive"),
        ("rival", "enemy"),
    ]
