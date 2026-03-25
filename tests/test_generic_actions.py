from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.generic_actions import parse_generic_action_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_market_generic_action_document(game_install: GameInstall) -> None:
    document = parse_generic_action_document(
        _read_text(game_install.representative_files()["generic_action_market_sample"])
    )

    relocate_market = document.get_definition("relocate_market")
    assert relocate_market is not None
    assert relocate_market.action_type == "owncountry"
    assert relocate_market.price == "price:relocate_market"
    assert len(relocate_market.select_triggers) == 2
    assert relocate_market.select_triggers[0].looking_for_a == "market"
    assert relocate_market.select_triggers[0].columns[0].data == "name"
    assert relocate_market.select_triggers[1].target_flag == "target_location"
    assert relocate_market.select_triggers[1].columns[1].data == "population"

    create_market = document.get_definition("create_market")
    assert create_market is not None
    assert create_market.should_execute_price is False
    assert create_market.price_modifier is not None
    assert create_market.select_triggers[0].source_flags == ("include_subjects",)


@pytest.mark.timeout(5)
def test_parse_real_secondary_generic_action_document(game_install: GameInstall) -> None:
    document = parse_generic_action_document(
        _read_text(game_install.representative_files()["generic_action_secondary_sample"])
    )

    change_employment_system = document.get_definition("change_employment_system")
    assert change_employment_system is not None
    assert change_employment_system.action_type == "owncountry"
    assert change_employment_system.ai_tick == "monthly"
    assert change_employment_system.ai_tick_frequency == "60"
    assert change_employment_system.select_triggers[0].looking_for_a == "employment_system"
    assert change_employment_system.effect is not None
    assert change_employment_system.ai_will_do is not None


def test_generic_action_parses_inline_select_triggers() -> None:
    document = parse_generic_action_document(
        "sample_action = {\n"
        "    type = owncountry\n"
        "    should_execute_price = no\n"
        "    select_trigger = {\n"
        "        looking_for_a = market\n"
        "        target_flag = target\n"
        "        source_flags = include_subjects\n"
        "        cache_targets = yes\n"
        "        column = {\n"
        "            data = name\n"
        "            width = 80\n"
        "            show_icon_in_cells = yes\n"
        "        }\n"
        "        visible = { owner ?= scope:actor }\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("sample_action")
    assert definition is not None
    assert definition.action_type == "owncountry"
    assert definition.should_execute_price is False
    assert len(definition.select_triggers) == 1

    select_trigger = definition.select_triggers[0]
    assert select_trigger.looking_for_a == "market"
    assert select_trigger.target_flag == "target"
    assert select_trigger.source_flags == ("include_subjects",)
    assert select_trigger.cache_targets is True
    assert len(select_trigger.columns) == 1
    assert select_trigger.columns[0].data == "name"
    assert select_trigger.columns[0].width == "80"
    assert select_trigger.columns[0].show_icon_in_cells is True
    assert select_trigger.visible is not None
