from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.scripted_relations import parse_scripted_relation_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_scripted_relation_document(game_install: GameInstall) -> None:
    document = parse_scripted_relation_document(
        _read_text(game_install.representative_files()["scripted_relation_sample"])
    )

    assert document.names() == ("alliance",)

    definition = document.get_definition("alliance")
    assert definition is not None
    assert definition.relation_kind == "diplomacy"
    assert definition.relation_type == "mutual"
    assert definition.uses_diplo_capacity == "mutual"
    assert definition.block_when_at_war is True
    assert definition.break_on_war is True
    assert definition.military_access is True
    assert definition.fleet_basing_rights is True
    assert definition.show_break_alert is True
    assert definition.mutual_color == "define:NMapColors|DIPLOMACY_ALLIANCE_COLOR"
    assert definition.category is not None
    assert definition.offer_enabled is not None
    assert definition.cancel_effect is not None
    assert definition.wants_to_give is not None
    assert definition.favors_to_first is None


@pytest.mark.timeout(5)
def test_parse_secondary_real_scripted_relation_document(game_install: GameInstall) -> None:
    document = parse_scripted_relation_document(
        _read_text(game_install.representative_files()["scripted_relation_secondary_sample"])
    )

    definition = document.get_definition("trade_access")
    assert definition is not None
    assert definition.relation_type == "oneway"
    assert definition.lifts_trade_protection is True
    assert definition.trade_to_first == "0.2"
    assert definition.request_enabled is not None
    assert definition.break_effect is not None
    assert definition.wants_to_receive is not None


def test_scripted_relation_parses_inline_fields() -> None:
    document = parse_scripted_relation_document(
        "example_relation = {\n"
        "    type = diplomacy\n"
        "    relation_type = mutual\n"
        "    uses_diplo_capacity = mutual\n"
        "    block_when_at_war = yes\n"
        "    mutual_color = rgb { 10 20 30 }\n"
        "    category = { offer = CATEGORY_FRIENDLY_ACTIONS }\n"
        "    offer_effect = { add_prestige = 5 }\n"
        "    wants_to_keep = { base = 10 }\n"
        "}\n"
    )

    definition = document.get_definition("example_relation")
    assert definition is not None
    assert definition.relation_kind == "diplomacy"
    assert definition.relation_type == "mutual"
    assert definition.uses_diplo_capacity == "mutual"
    assert definition.block_when_at_war is True
    assert definition.mutual_color == "rgb"
    assert definition.category is not None
    assert definition.offer_effect is not None
    assert definition.wants_to_keep is not None
