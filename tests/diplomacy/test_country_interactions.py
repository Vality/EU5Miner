from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.diplomacy.country_interactions import parse_country_interaction_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_country_interaction_document(game_install: GameInstall) -> None:
    document = parse_country_interaction_document(
        _read_text(game_install.representative_files()["country_interaction_sample"])
    )

    definition = document.get_definition("request_loan")
    assert definition is not None
    assert definition.interaction_type == "diplomacy"
    assert definition.category == "CATEGORY_ECONOMY_ACTIONS"
    assert definition.ai_tick == "never"
    assert definition.diplo_chance is not None
    assert len(definition.select_triggers) == 1
    assert definition.select_triggers[0].target_flag == "recipient"
    assert definition.ai_will_do == "-10"
    assert definition.effect is not None


@pytest.mark.timeout(5)
def test_parse_real_variant_country_interaction_document(game_install: GameInstall) -> None:
    document = parse_country_interaction_document(
        _read_text(game_install.representative_files()["country_interaction_secondary_sample"])
    )

    definition = document.get_definition("sell_icon")
    assert definition is not None
    assert definition.diplomatic_cost == "sell_icon_cost"
    assert definition.price == "price:sell_icon"
    assert definition.price_modifier is not None
    assert definition.payer == "scope:recipient"
    assert definition.payee == "scope:actor"
    assert len(definition.select_triggers) == 2
    assert definition.select_triggers[0].interaction_source_list is not None
    assert definition.select_triggers[1].cache_targets is True
    assert definition.accept is not None
    assert isinstance(definition.ai_will_do, SemanticObject)


def test_country_interaction_parses_inline_variant_fields() -> None:
    document = parse_country_interaction_document(
        "sample_country_interaction = {\n"
        "    type = diplomacy\n"
        "    ai_limit_per_check = 3\n"
        "    automation_tick = monthly\n"
        "    automation_tick_frequency = 6\n"
        "    ai_prerequisite = { always = yes }\n"
        "    reject_effect = { add_prestige = -1 }\n"
        "    is_take_over_loan = yes\n"
        "    accept = { add = 5 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_country_interaction")
    assert definition is not None
    assert definition.ai_limit_per_check == 3
    assert definition.automation_tick == "monthly"
    assert definition.automation_tick_frequency == "6"
    assert definition.ai_prerequisite is not None
    assert definition.reject_effect is not None
    assert definition.is_take_over_loan is True
    assert isinstance(definition.accept, SemanticObject)
