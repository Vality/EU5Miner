from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner import ContentPhase
from eu5miner.domains.diplomacy.casus_belli import parse_casus_belli_document
from eu5miner.domains.diplomacy.character_interactions import parse_character_interaction_document
from eu5miner.domains.diplomacy.country_interactions import parse_country_interaction_document
from eu5miner.domains.diplomacy.diplomacy import build_diplomacy_graph_catalog
from eu5miner.domains.diplomacy.peace_treaties import parse_peace_treaty_document
from eu5miner.domains.diplomacy.subject_types import parse_subject_type_document
from eu5miner.domains.diplomacy.wargoals import parse_wargoal_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_build_diplomacy_graph_catalog_collects_real_interaction_links(
    game_install: GameInstall,
) -> None:
    common_dir = game_install.phase_dir(ContentPhase.IN_GAME) / "common"
    country_break_union = parse_country_interaction_document(
        _read_text(common_dir / "country_interactions" / "break_union.txt")
    )
    country_samanta = parse_country_interaction_document(
        _read_text(common_dir / "country_interactions" / "samanta_upgrades.txt")
    )
    country_force_language = parse_country_interaction_document(
        _read_text(common_dir / "country_interactions" / "force_change_court_language.txt")
    )
    character_assign_governor = parse_character_interaction_document(
        _read_text(common_dir / "character_interactions" / "assign_governor.txt")
    )

    catalog = build_diplomacy_graph_catalog(
        casus_belli_documents=(
            parse_casus_belli_document("cb_claim_throne = { war_goal_type = sample_goal }\n"),
        ),
        wargoal_documents=(parse_wargoal_document("sample_goal = { type = superiority }\n"),),
        peace_treaty_documents=(),
        subject_type_documents=(
            parse_subject_type_document(
                "fiefdom = { level = 1 }\n"
                "maha_samanta = { level = 1 }\n"
                "pradhana_maha_samanta = { level = 2 }\n"
                "vassal = { level = 1 }\n"
            ),
        ),
        country_interaction_documents=(
            country_break_union,
            country_samanta,
            country_force_language,
        ),
        character_interaction_documents=(character_assign_governor,),
    )

    assert tuple(
        definition.name
        for definition in catalog.get_casus_belli_references_for_country_interaction(
            "break_subject_union"
        )
    ) == ("cb_claim_throne",)
    assert tuple(
        definition.name
        for definition in catalog.get_subject_type_references_for_country_interaction(
            "upgrade_to_maha_samanta"
        )
    ) == ("maha_samanta",)
    assert tuple(
        definition.name
        for definition in catalog.get_country_interaction_references_for_country_interaction(
            "force_change_court_language"
        )
    ) == ("force_change_court_language",)
    assert tuple(
        definition.name
        for definition in catalog.get_subject_type_references_for_character_interaction(
            "assign_governor"
        )
    ) == ("vassal",)


def test_build_diplomacy_graph_report_summarizes_links_and_missing_references() -> None:
    catalog = build_diplomacy_graph_catalog(
        casus_belli_documents=(
            parse_casus_belli_document("cb_example = { war_goal_type = sample_goal }\n"),
        ),
        wargoal_documents=(parse_wargoal_document("sample_goal = { type = superiority }\n"),),
        peace_treaty_documents=(
            parse_peace_treaty_document(
                "peace_example = {\n"
                "    potential = { scope:war = { casus_belli ?= casus_belli:cb_example } }\n"
                "    effect = { make_subject_of = { type = subject_type:sample_subject } }\n"
                "}\n"
            ),
        ),
        subject_type_documents=(
            parse_subject_type_document("sample_subject = { level = 1 }\n"),
        ),
        country_interaction_documents=(
            parse_country_interaction_document(
                "country_link = {\n"
                "    effect = { add_casus_belli = { type = casus_belli:cb_example } }\n"
                "}\n"
                "subject_link = {\n"
                "    effect = { make_subject_of = { type = subject_type:sample_subject } }\n"
                "}\n"
                "interaction_link = {\n"
                "    ai_will_do = { add = \"scope:actor.country_interaction_acceptance(country_interaction:country_link|scope:recipient)\" }\n"
                "}\n"
                "missing_link = {\n"
                "    effect = { add_casus_belli = { type = casus_belli:cb_missing } }\n"
                "}\n"
            ),
        ),
        character_interaction_documents=(
            parse_character_interaction_document(
                "character_link = {\n"
                "    effect = { make_subject_of = { type = subject_type:sample_subject } }\n"
                "}\n"
            ),
        ),
    )

    report = catalog.build_report()

    assert tuple(edge.source_name for edge in report.peace_treaty_casus_belli_links) == (
        "peace_example",
    )
    assert tuple(edge.source_name for edge in report.country_interaction_casus_belli_links) == (
        "country_link",
        "missing_link",
    )
    assert tuple(edge.source_name for edge in report.country_interaction_subject_type_links) == (
        "subject_link",
    )
    assert tuple(edge.source_name for edge in report.character_interaction_subject_type_links) == (
        "character_link",
    )
    assert tuple(edge.source_name for edge in report.country_interaction_links) == (
        "interaction_link",
    )
    assert report.missing_casus_belli_references == ("cb_missing",)
    assert report.missing_subject_type_references == ()
    assert report.missing_country_interaction_references == ()

    assert tuple(
        definition.name for definition in catalog.get_country_interactions_for_casus_belli("cb_example")
    ) == ("country_link",)
    assert tuple(
        definition.name for definition in catalog.get_country_interactions_for_subject_type("sample_subject")
    ) == ("subject_link",)
    assert tuple(
        definition.name for definition in catalog.get_character_interactions_for_subject_type("sample_subject")
    ) == ("character_link",)
