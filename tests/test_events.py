from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.events import parse_event_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_event_document(game_install: GameInstall) -> None:
    document = parse_event_document(_read_text(game_install.representative_files()["event_sample"]))

    assert document.namespace == "civil_war"
    assert document.event_ids() == ("civil_war.1",)

    definition = document.get_definition("civil_war.1")
    assert definition is not None
    assert definition.namespace == "civil_war"
    assert definition.event_number == "1"
    assert definition.event_type == "country_event"
    assert definition.title == "civil_war.1.title"
    assert definition.desc == "civil_war.1.desc"
    assert definition.trigger is not None
    assert definition.after is not None
    assert len(definition.options) == 2
    assert definition.options[0].name == "civil_war.1.a"
    assert definition.options[1].name == "civil_war.1.b"


def test_parse_event_document_with_alternative_title_and_desc_blocks() -> None:
    document = parse_event_document(
        "namespace = sample_events\n"
        "sample_events.1 = {\n"
        "    type = country_event\n"
        "    title = {\n"
        "        first_valid = {\n"
        "            triggered_desc = {\n"
        "                desc = sample_events.1.title.a\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "    desc = {\n"
        "        first_valid = {\n"
        "            triggered_desc = {\n"
        "                desc = sample_events.1.desc.a\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "    hidden = yes\n"
        "    fire_only_once = no\n"
        "    immediate = { add_stability = 1 }\n"
        "    option = {\n"
        "        name = sample_events.1.a\n"
        "        fallback = yes\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("sample_events.1")
    assert definition is not None
    assert definition.title is None
    assert definition.title_object is not None
    assert definition.desc is None
    assert definition.desc_object is not None
    assert definition.hidden is True
    assert definition.fire_only_once is False
    assert definition.immediate is not None
    assert len(definition.options) == 1
    assert definition.options[0].fallback is True


def test_parse_event_document_with_option_flags() -> None:
    document = parse_event_document(
        "namespace = sample_events\n"
        "sample_events.2 = {\n"
        "    type = country_event\n"
        "    title = sample_events.2.title\n"
        "    desc = sample_events.2.desc\n"
        "    major = yes\n"
        "    option = {\n"
        "        name = sample_events.2.a\n"
        "        historical_option = yes\n"
        "        exclusive = yes\n"
        "        original_recipient_only = no\n"
        "        ai_chance = { base = 1 }\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("sample_events.2")
    assert definition is not None
    assert definition.major is True
    assert len(definition.options) == 1

    option = definition.options[0]
    assert option.name == "sample_events.2.a"
    assert option.historical_option is True
    assert option.exclusive is True
    assert option.original_recipient_only is False
    assert option.ai_chance is not None
