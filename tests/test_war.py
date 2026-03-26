from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.casus_belli import parse_casus_belli_document
from eu5miner.domains.peace_treaties import parse_peace_treaty_document
from eu5miner.domains.subject_types import parse_subject_type_document
from eu5miner.domains.war import (
    build_war_flow_catalog,
    collect_casus_belli_references,
    collect_subject_type_references,
)
from eu5miner.domains.wargoals import parse_wargoal_document
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
