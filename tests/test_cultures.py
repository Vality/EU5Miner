from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.cultures import parse_culture_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_culture_document(game_install: GameInstall) -> None:
    document = parse_culture_document(
        _read_text(game_install.representative_files()["culture_sample"])
    )

    assert len(document.definitions) > 5
    assert document.definitions[0].name == "english"

    definition = document.get_definition("highland")
    assert definition is not None
    assert definition.language == "scottish_gaelic_dialect"
    assert definition.color == "map_highland"
    assert definition.use_patronym is True
    assert definition.dynasty_name_type == "patronym"
    assert "celtic_group" in definition.culture_groups
    assert "scottish_highland_gfx" in definition.tags


def test_culture_document_parses_lists_and_opinions() -> None:
    document = parse_culture_document(
        "example_culture = {\n"
        "    language = example_language\n"
        "    color = map_EXA\n"
        "    tags = { alpha beta }\n"
        "    culture_groups = { group_a group_b }\n"
        "    opinions = {\n"
        "        other = kindred\n"
        "        rival = enemy\n"
        "    }\n"
        "    noun_keys = { one two }\n"
        "    adjective_keys = { red blue }\n"
        "    use_patronym = no\n"
        "    dynasty_name_type = descendant\n"
        "}\n"
    )

    definition = document.get_definition("example_culture")
    assert definition is not None
    assert definition.tags == ("alpha", "beta")
    assert definition.culture_groups == ("group_a", "group_b")
    assert definition.noun_keys == ("one", "two")
    assert definition.adjective_keys == ("red", "blue")
    assert definition.use_patronym is False
    assert [(opinion.culture, opinion.stance) for opinion in definition.opinions] == [
        ("other", "kindred"),
        ("rival", "enemy"),
    ]
