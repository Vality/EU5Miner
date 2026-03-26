from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.diplomacy.casus_belli import parse_casus_belli_document
from eu5miner.domains.diplomacy.peace_treaties import parse_peace_treaty_document
from eu5miner.domains.diplomacy.subject_types import parse_subject_type_document
from eu5miner.domains.diplomacy import (
    build_war_flow_catalog,
    build_war_flow_report,
    collect_casus_belli_references,
    collect_country_interaction_references,
    collect_subject_type_references,
    WarFlowReport,
)
from eu5miner.domains.diplomacy.wargoals import parse_wargoal_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_build_war_flow_catalog_links_real_subject_chain(game_install: GameInstall) -> None:
    catalog = build_war_flow_catalog(
        casus_belli_documents=(
            parse_casus_belli_document(
                _read_text(game_install.representative_files()["casus_belli_subject_sample"])
            ),
        ),
        wargoal_documents=(
            parse_wargoal_document(_read_text(game_install.representative_files()["wargoal_sample"])),
        ),
        peace_treaty_documents=(
            parse_peace_treaty_document(
                _read_text(game_install.representative_files()["peace_treaty_secondary_sample"])
            ),
        ),
        subject_type_documents=(
            parse_subject_type_document(
                _read_text(game_install.representative_files()["subject_type_secondary_sample"])
            ),
        ),
    )

    wargoal = catalog.get_wargoal_for_casus_belli("cb_make_tributary")
    assert wargoal is not None
    assert wargoal.name == "take_capital_tributary"

    peace_treaties = catalog.get_peace_treaties_for_casus_belli("cb_make_tributary")
    assert tuple(definition.name for definition in peace_treaties) == ("force_tributary",)

    by_wargoal = catalog.get_peace_treaties_for_wargoal("take_capital_tributary")
    assert tuple(definition.name for definition in by_wargoal) == ("force_tributary",)

    subject_types = catalog.get_subject_type_references_for_peace_treaty("force_tributary")
    assert tuple(definition.name for definition in subject_types) == ("tributary",)


@pytest.mark.timeout(5)
def test_collect_casus_belli_references_and_religious_chain(game_install: GameInstall) -> None:
    peace_treaty_document = parse_peace_treaty_document(
        _read_text(game_install.representative_files()["peace_treaty_special_sample"])
    )
    casus_belli_document = parse_casus_belli_document(
        _read_text(game_install.representative_files()["casus_belli_religious_sample"])
    )
    wargoal_document = parse_wargoal_document(
        _read_text(game_install.representative_files()["wargoal_sample"])
    )

    religious_supremacy = peace_treaty_document.get_definition("religious_supremacy")
    assert religious_supremacy is not None
    assert collect_casus_belli_references(religious_supremacy.body) == (
        "cb_religious_superiority",
    )
    assert collect_subject_type_references(religious_supremacy.body) == ()

    catalog = build_war_flow_catalog(
        casus_belli_documents=(casus_belli_document,),
        wargoal_documents=(wargoal_document,),
        peace_treaty_documents=(peace_treaty_document,),
        subject_type_documents=(),
    )

    linked = catalog.get_casus_belli_references_for_peace_treaty("religious_supremacy")
    assert tuple(definition.name for definition in linked) == ("cb_religious_superiority",)

    wargoal = catalog.get_wargoal_for_casus_belli("cb_religious_superiority")
    assert wargoal is not None
    assert wargoal.name == "religious_superiority_wargoal"


def test_build_war_flow_catalog_links_inline_documents() -> None:
    casus_belli_document = parse_casus_belli_document(
        "cb_example = { war_goal_type = example_goal }\n"
    )
    wargoal_document = parse_wargoal_document(
        "example_goal = { type = superiority }\n"
    )
    peace_treaty_document = parse_peace_treaty_document(
        "peace_example = { potential = { scope:war = { casus_belli ?= casus_belli:cb_example } } }\n"
    )

    catalog = build_war_flow_catalog(
        casus_belli_documents=(casus_belli_document,),
        wargoal_documents=(wargoal_document,),
        peace_treaty_documents=(peace_treaty_document,),
        subject_type_documents=(),
    )

    assert catalog.get_wargoal_for_casus_belli("cb_example") is not None
    assert tuple(definition.name for definition in catalog.get_peace_treaties_for_wargoal("example_goal")) == (
        "peace_example",
    )

    report = build_war_flow_report(catalog)
    assert tuple(edge.source_name for edge in report.casus_belli_wargoal_links) == ("cb_example",)
    assert tuple(edge.source_name for edge in report.peace_treaty_casus_belli_links) == (
        "peace_example",
    )
    assert report.missing_wargoal_references == ()
    assert report.missing_casus_belli_references == ()
    assert report.missing_subject_type_references == ()
    assert isinstance(report, WarFlowReport)


def test_collect_country_interaction_references_from_embedded_string() -> None:
    peace_treaty_document = parse_peace_treaty_document(
        "peace_example = { effect = { log = \"country_interaction:send_warning|scope:recipient\" } }\n"
    )

    assert collect_country_interaction_references(peace_treaty_document.definitions[0].body) == (
        "send_warning",
    )


def test_build_war_flow_report_collects_missing_references() -> None:
    catalog = build_war_flow_catalog(
        casus_belli_documents=(
            parse_casus_belli_document("cb_example = { war_goal_type = missing_goal }\n"),
        ),
        wargoal_documents=(parse_wargoal_document("resolved_goal = { type = superiority }\n"),),
        peace_treaty_documents=(
            parse_peace_treaty_document(
                "peace_example = {\n"
                "    potential = { scope:war = { casus_belli ?= casus_belli:missing_cb } }\n"
                "    effect = { make_subject_of = { type = subject_type:missing_subject } }\n"
                "}\n"
            ),
        ),
        subject_type_documents=(parse_subject_type_document("resolved_subject = { level = 1 }\n"),),
    )

    report = catalog.build_report()

    assert tuple(edge.source_name for edge in report.casus_belli_wargoal_links) == ("cb_example",)
    assert tuple(edge.source_name for edge in report.peace_treaty_casus_belli_links) == (
        "peace_example",
    )
    assert tuple(edge.source_name for edge in report.peace_treaty_subject_type_links) == (
        "peace_example",
    )
    assert report.missing_wargoal_references == ("missing_goal",)
    assert report.missing_casus_belli_references == ("missing_cb",)
    assert report.missing_subject_type_references == ("missing_subject",)
