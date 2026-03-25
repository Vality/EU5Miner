from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.on_actions import (
    build_on_action_catalog_document,
    parse_on_action_document,
    parse_on_action_documentation,
)
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_on_action_document(game_install: GameInstall) -> None:
    document = parse_on_action_document(
        _read_text(game_install.representative_files()["on_action_sample"])
    )

    assert document.names() == ("religion_flavor_pulse",)

    definition = document.get_definition("religion_flavor_pulse")
    assert definition is not None
    assert tuple(reference.name for reference in definition.events) == (
        "flavor_pap.1502",
        "orthodox_flavor.11",
    )
    assert definition.random_events is not None
    assert len(definition.random_events.weighted_events) > 50
    assert definition.random_events.weighted_events[0].weight == 10
    assert definition.random_events.weighted_events[0].event == "muslim_flavor.1"
    assert definition.random_events.chance_to_happen == "50"


@pytest.mark.timeout(5)
def test_parse_secondary_real_on_action_document(game_install: GameInstall) -> None:
    document = parse_on_action_document(
        _read_text(game_install.representative_files()["on_action_secondary_sample"])
    )

    on_character_death = document.get_definition("on_character_death")
    assert on_character_death is not None
    assert tuple(reference.name for reference in on_character_death.on_actions) == (
        "on_cabinet_death",
        "on_horde_pretender_death",
        "on_tamil_rebel_death",
        "on_prussian_crusader_death",
    )
    assert on_character_death.effect is not None

    on_cabinet_death = document.get_definition("on_cabinet_death")
    assert on_cabinet_death is not None
    assert on_cabinet_death.trigger is not None
    assert on_cabinet_death.effect is not None


def test_on_action_parses_inline_fields_and_parameters() -> None:
    document = parse_on_action_document(
        "on_example = {\n"
        "    on_actions = { on_child_hook }\n"
        "    events = { event_namespace.1 }\n"
        "    random_events = {\n"
        "        25 = event_namespace.2\n"
        "        chance_to_happen = $MONTHS$\n"
        "        chance_of_no_event = { value = 50 }\n"
        "    }\n"
        "    trigger = { exists = $TARGET$ }\n"
        "    effect = { add_prestige = 5 }\n"
        "}\n"
    )

    definition = document.get_definition("on_example")
    assert definition is not None
    assert tuple(reference.name for reference in definition.on_actions) == ("on_child_hook",)
    assert tuple(reference.name for reference in definition.events) == ("event_namespace.1",)
    assert definition.random_events is not None
    assert definition.random_events.weighted_events[0].weight == 25
    assert definition.random_events.weighted_events[0].event == "event_namespace.2"
    assert definition.random_events.chance_to_happen == "$MONTHS$"
    assert definition.random_events.chance_of_no_event is not None
    assert definition.trigger is not None
    assert definition.effect is not None
    assert definition.parameters == ("MONTHS", "TARGET")


def test_on_action_documentation_and_catalog_cross_link() -> None:
    documentation = parse_on_action_documentation(
        "On Action Documentation:\n\n"
        "--------------------\n\n"
        "yearly_country_pulse:\n"
        "From Code: Yes\n"
        "Expected Scope: country\n\n"
        "--------------------\n\n"
        "on_tamil_rebel_death:\n"
        "From Code: No\n"
        "Expected Scope: none\n"
    )
    document = parse_on_action_document(
        "yearly_country_pulse = { events = { flavor_test.1 } }\n"
        "on_tamil_rebel_death = { effect = { add_stability = 1 } }\n"
    )
    catalog = build_on_action_catalog_document([document], documentation)

    documented = documentation.get_definition("yearly_country_pulse")
    assert documented is not None
    assert documented.from_code is True
    assert documented.expected_scope == "country"

    catalog_entry = catalog.get_entry("on_tamil_rebel_death")
    assert catalog_entry is not None
    assert len(catalog_entry.definitions) == 1
    assert catalog_entry.documentation is not None
    assert catalog_entry.documentation.from_code is False
    assert catalog_entry.documentation.expected_scope == "none"
