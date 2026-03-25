from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.scripted_lists import parse_scripted_list_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_scripted_list_document(game_install: GameInstall) -> None:
    document = parse_scripted_list_document(
        _read_text(game_install.representative_files()["scripted_list_sample"])
    )

    assert len(document.definitions) >= 3

    definition = document.get_definition("junior_partner")
    assert definition is not None
    assert definition.base == "union_partner"
    assert definition.conditions is not None
    assert definition.conditions.first_entry("PREV") is not None


def test_scripted_list_parses_base_conditions_and_parameters() -> None:
    document = parse_scripted_list_document(
        "adult_character = {\n"
        "    base = character\n"
        "    conditions = {\n"
        "        is_adult = yes\n"
        "        is_in_scope_of = $TARGET$\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("adult_character")
    assert definition is not None
    assert definition.base == "character"
    assert definition.conditions is not None
    assert definition.conditions.get_scalar("is_adult") == "yes"
    assert definition.parameters == ("TARGET",)
