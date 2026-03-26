from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.diplomacy.wargoals import parse_wargoal_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_wargoal_document(game_install: GameInstall) -> None:
    document = parse_wargoal_document(
        _read_text(game_install.representative_files()["wargoal_sample"])
    )

    take_country = document.get_definition("take_country")
    assert take_country is not None
    assert take_country.war_goal_type == "take_country"
    assert take_country.attacker is not None
    assert take_country.attacker.conquer_cost == "0.5"
    assert take_country.attacker.subjugate_cost == "0.5"
    assert take_country.defender is not None


@pytest.mark.timeout(5)
def test_parse_real_wargoal_sparse_fields(game_install: GameInstall) -> None:
    document = parse_wargoal_document(
        _read_text(game_install.representative_files()["wargoal_sample"])
    )

    colony_war = document.get_definition("take_capital_colony_war")
    assert colony_war is not None
    assert colony_war.war_name == '"COLONIAL_WAR_NAME"'
    assert colony_war.attacker is not None
    assert colony_war.attacker.call_in_overlord is False
    assert colony_war.attacker.allowed_subjugation is not None
    assert colony_war.defender is not None
    assert colony_war.defender.call_in_overlord is False

    hundred_years_war = document.get_definition("hundred_years_war_wargoal")
    assert hundred_years_war is not None
    assert hundred_years_war.war_name_is_country_order_agnostic is True
    assert hundred_years_war.attacker is not None
    assert hundred_years_war.attacker.allowed_locations is not None


def test_wargoal_parses_inline_participant_fields() -> None:
    document = parse_wargoal_document(
        "sample_goal = {\n"
        "    type = superiority\n"
        "    war_name_is_country_order_agnostic = yes\n"
        "    attacker = {\n"
        "        call_in_subjects = no\n"
        "        antagonism = 1.25\n"
        "        allowed_locations = { always = yes }\n"
        "    }\n"
        "    defender = {\n"
        "        subjugate_cost = 0.5\n"
        "    }\n"
        "    ticking_war_score = 0.75\n"
        "}\n"
    )

    definition = document.get_definition("sample_goal")
    assert definition is not None
    assert definition.war_goal_type == "superiority"
    assert definition.war_name_is_country_order_agnostic is True
    assert definition.attacker is not None
    assert definition.attacker.call_in_subjects is False
    assert definition.attacker.antagonism == "1.25"
    assert definition.attacker.allowed_locations is not None
    assert definition.defender is not None
    assert definition.defender.subjugate_cost == "0.5"
    assert definition.ticking_war_score == "0.75"
