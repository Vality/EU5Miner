from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.scripted_modifiers import parse_scripted_modifier_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_info_example_modifier(text: str) -> str:
    marker = "example_modifier = {"
    start = text.index(marker)
    end = text.index("== Example invocation ==")
    return text[start:end].strip() + "\n"


@pytest.mark.timeout(5)
def test_parse_real_scripted_modifier_example_from_info(game_install: GameInstall) -> None:
    info_text = _read_text(game_install.representative_files()["scripted_modifier_info"])
    document = parse_scripted_modifier_document(_extract_info_example_modifier(info_text))

    assert document.names() == ("example_modifier",)

    definition = document.get_definition("example_modifier")
    assert definition is not None
    assert definition.modifier is not None
    assert definition.opinion_modifier is not None
    assert definition.compare_modifier is not None
    assert definition.modifier.get_object("add") is not None
    assert definition.parameters == ("CHARACTER_1", "CHARACTER_2", "SCALE")


def test_scripted_modifier_parses_modifier_blocks_and_parameters() -> None:
    document = parse_scripted_modifier_document(
        "approval_modifier_grateful_family = {\n"
        "    modifier = {\n"
        "        trigger = { any_family = { is_grateful = yes } }\n"
        "        add = { every_family = { add = $VALUE$ } }\n"
        "        desc = APPROVAL_MODIFIER_GRATEFUL_FAMILY\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("approval_modifier_grateful_family")
    assert definition is not None
    assert definition.modifier is not None
    assert definition.modifier.get_object("trigger") is not None
    assert definition.modifier.get_object("add") is not None
    assert definition.modifier.get_scalar("desc") == "APPROVAL_MODIFIER_GRATEFUL_FAMILY"
    assert definition.opinion_modifier is None
    assert definition.compare_modifier is None
    assert definition.parameters == ("VALUE",)


def test_scripted_modifier_allows_multiple_modifier_types() -> None:
    document = parse_scripted_modifier_document(
        "my_modifier = {\n"
        "    modifier = { add = 10 }\n"
        "    opinion_modifier = { target = root who = scope:actor multiplier = 0.5 }\n"
        "    compare_modifier = { target = root value = stress multiplier = 2 }\n"
        "}\n"
    )

    definition = document.get_definition("my_modifier")
    assert definition is not None
    assert definition.modifier is not None
    assert definition.opinion_modifier is not None
    assert definition.compare_modifier is not None
