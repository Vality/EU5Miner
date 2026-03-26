from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.casus_belli import parse_casus_belli_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_casus_belli_document(game_install: GameInstall) -> None:
    document = parse_casus_belli_document(
        _read_text(game_install.representative_files()["casus_belli_sample"])
    )

    definition = document.get_definition("cb_conquer_province")
    assert definition is not None
    assert definition.war_goal_type == "conquer_province"
    assert definition.allow_creation is not None
    assert definition.province is not None
    assert definition.visible is None
    assert definition.trade is None


@pytest.mark.timeout(5)
def test_parse_real_sparse_casus_belli_documents(game_install: GameInstall) -> None:
    hardcoded = parse_casus_belli_document(
        _read_text(game_install.representative_files()["casus_belli_secondary_sample"])
    )
    coalition = parse_casus_belli_document(
        _read_text(game_install.representative_files()["casus_belli_dense_sample"])
    )
    trade = parse_casus_belli_document(
        _read_text(game_install.representative_files()["casus_belli_trade_sample"])
    )

    cb_none = hardcoded.get_definition("cb_none")
    assert cb_none is not None
    assert cb_none.no_cb is True
    assert cb_none.allow_declaration is not None
    assert cb_none.war_goal_type == "superiority"

    follow_through = hardcoded.get_definition("cb_following_through_on_threat")
    assert follow_through is not None
    assert follow_through.cut_down_in_size_cb is True
    assert follow_through.ai_subjugation_desire == "-100"
    assert follow_through.allow_release_areas is True

    cb_coalition = coalition.get_definition("cb_coalition")
    assert cb_coalition is not None
    assert cb_coalition.additional_war_enthusiasm_attacker == "0.25"
    assert cb_coalition.antagonism_reduction_per_warworth_defender == "0.5"
    assert cb_coalition.allow_separate_peace is False
    assert cb_coalition.can_expire is False

    cb_trade_conflict = trade.get_definition("cb_trade_conflict")
    assert cb_trade_conflict is not None
    assert cb_trade_conflict.trade is True
    assert cb_trade_conflict.war_goal_type == "naval"


def test_casus_belli_parses_inline_variant_fields() -> None:
    document = parse_casus_belli_document(
        "sample_cb = {\n"
        "    visible = { always = yes }\n"
        "    ai_cede_location_desire = { add = { value = 50 } }\n"
        "    custom_tags = { religious_casus_belli holy_war }\n"
        "    trade = yes\n"
        "    war_goal_type = superiority\n"
        "}\n"
    )

    definition = document.get_definition("sample_cb")
    assert definition is not None
    assert definition.visible is not None
    assert isinstance(definition.ai_cede_location_desire, SemanticObject)
    assert definition.custom_tags == ("religious_casus_belli", "holy_war")
    assert definition.trade is True
    assert definition.war_goal_type == "superiority"