from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.diplomacy.character_interactions import parse_character_interaction_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_character_interaction_document(game_install: GameInstall) -> None:
    document = parse_character_interaction_document(
        _read_text(game_install.representative_files()["character_interaction_sample"])
    )

    definition = document.get_definition("abdicate")
    assert definition is not None
    assert definition.message is True
    assert definition.is_consort_action is False
    assert definition.on_own_nation is True
    assert definition.price == "price:abdicate_price"
    assert definition.price_modifier is not None
    assert definition.ai_tick == "daily"
    assert definition.ai_tick_frequency == "120"
    assert len(definition.select_triggers) == 1
    assert definition.select_triggers[0].source == "actor"
    assert definition.effect is not None
    assert isinstance(definition.ai_will_do, SemanticObject)


@pytest.mark.timeout(5)
def test_parse_real_variant_character_interaction_documents(game_install: GameInstall) -> None:
    secondary = parse_character_interaction_document(
        _read_text(game_install.representative_files()["character_interaction_secondary_sample"])
    )
    ui = parse_character_interaction_document(
        _read_text(game_install.representative_files()["character_interaction_ui_sample"])
    )

    move_child = secondary.get_definition("move_child_to_court")
    assert move_child is not None
    assert move_child.on_other_nation is True
    assert move_child.message is True
    assert move_child.ai_tick == "never"
    assert move_child.ai_will_do is not None

    marry_noble = ui.get_definition("marry_noble")
    assert marry_noble is not None
    assert marry_noble.sound == "UI_action_character_marry_noble"
    assert marry_noble.context_menu_click_mode == "click"
    assert len(marry_noble.select_triggers) == 2
    assert marry_noble.select_triggers[1].top_widget == "marry_noble_character_top"
    assert marry_noble.select_triggers[1].none_available_msg_key == '"marry_noble_no_characters"'


def test_character_interaction_parses_inline_variant_fields() -> None:
    document = parse_character_interaction_document(
        "sample_character_interaction = {\n"
        "    message = no\n"
        "    on_other_nation = yes\n"
        "    show_in_gui_list = no\n"
        "    ai_will_do = -5\n"
        "    select_trigger = {\n"
        "        looking_for_a = character\n"
        "        allow_null = yes\n"
        "        allow_null_trigger = { always = yes }\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("sample_character_interaction")
    assert definition is not None
    assert definition.message is False
    assert definition.on_other_nation is True
    assert definition.show_in_gui_list is False
    assert definition.ai_will_do == "-5"
    assert definition.select_triggers[0].allow_null is True
    assert definition.select_triggers[0].allow_null_trigger is not None
