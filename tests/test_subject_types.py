from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.subject_types import parse_subject_type_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_subject_type_document(game_install: GameInstall) -> None:
    document = parse_subject_type_document(
        _read_text(game_install.representative_files()["subject_type_sample"])
    )

    definition = document.get_definition("vassal")
    assert definition is not None
    assert definition.level == 2
    assert definition.annullment_favours_required == 20
    assert definition.visible_through_diplomacy is not None
    assert definition.join_defensive_wars_always is not None
    assert definition.has_overlords_ruler is False
    assert definition.annexation_min_years_before == 10
    assert definition.food_access is True
    assert definition.minimum_opinion_for_offer == 150
    assert definition.overlord_modifier is not None
    assert definition.diplo_chance_accept_subject is not None


@pytest.mark.timeout(5)
def test_parse_real_variant_subject_type_documents(game_install: GameInstall) -> None:
    tributary_document = parse_subject_type_document(
        _read_text(game_install.representative_files()["subject_type_secondary_sample"])
    )
    colonial_document = parse_subject_type_document(
        _read_text(game_install.representative_files()["subject_type_colonial_sample"])
    )
    hre_document = parse_subject_type_document(
        _read_text(game_install.representative_files()["subject_type_hre_sample"])
    )
    special_document = parse_subject_type_document(
        _read_text(game_install.representative_files()["subject_type_special_sample"])
    )

    tributary = tributary_document.get_definition("tributary")
    assert tributary is not None
    assert tributary.can_be_annexed is False
    assert tributary.subject_can_cancel is True
    assert tributary.allow_declaring_wars is not None
    assert tributary.use_overlord_map_color is False
    assert tributary.use_overlord_map_name is False

    colonial_nation = colonial_document.get_definition("colonial_nation")
    assert colonial_nation is not None
    assert colonial_nation.is_colonial_subject is True
    assert colonial_nation.allow_subjects is False
    assert colonial_nation.overlord_share_exploration is True
    assert colonial_nation.merchants_to_overlord_fraction == 0.33
    assert colonial_nation.can_rival is not None
    assert colonial_nation.subject_creation_enabled is not None
    assert colonial_nation.government == "republic"

    imperial_free_city = hre_document.get_definition("imperial_free_city")
    assert imperial_free_city is not None
    assert imperial_free_city.subject_kind == "location"
    assert imperial_free_city.can_be_force_broken_in_peace_treaty is False
    assert imperial_free_city.overlord_can_enforce_peace_on_subject is True
    assert imperial_free_city.can_overlord_recruit_regiments is True

    appanage = special_document.get_definition("appanage")
    assert appanage is not None
    assert appanage.overlord_inherit_if_no_heir is True
    assert appanage.can_attack is not None
    assert appanage.enabled_through_diplomacy is not None


def test_subject_type_parses_inline_variant_fields() -> None:
    document = parse_subject_type_document(
        "sample_subject = {\n"
        "    subject_pays = { gold = 1 }\n"
        "    war_score_cost = { value = 25 }\n"
        "    allow_subjects = no\n"
        "    on_monthly = { add_prestige = 1 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_subject")
    assert definition is not None
    assert isinstance(definition.subject_pays, SemanticObject)
    assert isinstance(definition.war_score_cost, SemanticObject)
    assert definition.allow_subjects is False
    assert definition.on_monthly is not None
