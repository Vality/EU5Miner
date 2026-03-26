from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.government.estate_privileges import parse_estate_privilege_document
from eu5miner.domains.government.estates import parse_estate_document
from eu5miner.domains.government import build_government_catalog
from eu5miner.domains.government.government_reforms import parse_government_reform_document
from eu5miner.domains.government.government_types import parse_government_type_document
from eu5miner.domains.government.laws import parse_law_document
from eu5miner.domains.government.parliament_agendas import parse_parliament_agenda_document
from eu5miner.domains.government.parliament_issues import parse_parliament_issue_document
from eu5miner.domains.government.parliament_types import parse_parliament_type_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_build_government_catalog_links_real_family_definitions(
    game_install: GameInstall,
) -> None:
    catalog = build_government_catalog(
        government_type_documents=(
            parse_government_type_document(
                _read_text(game_install.representative_files()["government_type_sample"])
            ),
        ),
        government_reform_documents=(
            parse_government_reform_document(
                _read_text(game_install.representative_files()["government_reform_sample"])
            ),
            parse_government_reform_document(
                _read_text(game_install.representative_files()["government_reform_secondary_sample"])
            ),
        ),
        law_documents=(
            parse_law_document(_read_text(game_install.representative_files()["law_sample"])),
            parse_law_document(
                _read_text(game_install.representative_files()["law_secondary_sample"])
            ),
        ),
        estate_documents=(
            parse_estate_document(_read_text(game_install.representative_files()["estate_sample"])),
        ),
        estate_privilege_documents=(
            parse_estate_privilege_document(
                _read_text(game_install.representative_files()["estate_privilege_sample"])
            ),
            parse_estate_privilege_document(
                _read_text(game_install.representative_files()["estate_privilege_special_sample"])
            ),
        ),
        parliament_type_documents=(
            parse_parliament_type_document(
                _read_text(game_install.representative_files()["parliament_type_sample"])
            ),
            parse_parliament_type_document(
                _read_text(game_install.representative_files()["parliament_type_secondary_sample"])
            ),
        ),
        parliament_agenda_documents=(
            parse_parliament_agenda_document(
                _read_text(game_install.representative_files()["parliament_agenda_sample"])
            ),
            parse_parliament_agenda_document(
                _read_text(game_install.representative_files()["parliament_agenda_special_sample"])
            ),
        ),
        parliament_issue_documents=(
            parse_parliament_issue_document(
                _read_text(game_install.representative_files()["parliament_issue_sample"])
            ),
            parse_parliament_issue_document(
                _read_text(game_install.representative_files()["parliament_issue_special_sample"])
            ),
        ),
    )

    default_estate = catalog.get_default_estate_for_government("monarchy")
    assert default_estate is not None
    assert default_estate.name == "nobles_estate"

    assert "revolutionary_empire" in {
        definition.name for definition in catalog.get_reforms_for_government("monarchy")
    }
    assert "royal_court_customs_law" in {
        definition.name for definition in catalog.get_laws_for_government("monarchy")
    }
    assert "forums_of_thought" in {
        definition.name for definition in catalog.get_policies_for_estate("burghers_estate")
    }
    assert "auxilium_et_consilium" in {
        definition.name for definition in catalog.get_privileges_for_estate("nobles_estate")
    }
    assert "assembly" in {
        definition.name for definition in catalog.get_country_parliament_types()
    }
    assert "hre_court_assembly" in {
        definition.name for definition in catalog.get_international_organization_parliament_types()
    }
    assert "pa_add_privilege" in {
        definition.name for definition in catalog.get_parliament_agendas_for_estate(
            "nobles_estate"
        )
    }
    assert "pa_hre_elevate_prussia_to_kingdom" in {
        definition.name for definition in catalog.get_parliament_agendas_for_special_status(
            "elector"
        )
    }
    assert "bolster_the_monarchy" in {
        definition.name for definition in catalog.get_parliament_issues_for_estate(
            "crown_estate"
        )
    }
    assert "hre_law_debate" in {
        definition.name for definition in catalog.get_parliament_issues_for_special_status(
            "emperor"
        )
    }

    report = catalog.build_report()
    assert report.missing_government_type_references == ()
    assert report.missing_estate_references == ()
    assert "monarchy" in {
        reference
        for edge in report.reform_government_links
        if edge.source_name == "revolutionary_empire"
        for reference in edge.referenced_names
    }
    assert "nobles_estate" in {
        reference
        for edge in report.government_type_default_estate_links
        if edge.source_name == "monarchy"
        for reference in edge.referenced_names
    }


def test_build_government_report_collects_missing_references() -> None:
    catalog = build_government_catalog(
        government_type_documents=(
            parse_government_type_document(
                "monarchy = { default_character_estate = missing_estate }\n"
            ),
        ),
        government_reform_documents=(
            parse_government_reform_document(
                "sample_reform = { government = missing_government }\n"
            ),
        ),
        law_documents=(
            parse_law_document(
                "sample_law = {\n"
                "    law_category = administrative\n"
                "    law_gov_group = monarchy\n"
                "    law_gov_group = missing_government\n"
                "    policy_a = { estate_preferences = { nobles_estate missing_estate } }\n"
                "}\n"
            ),
        ),
        estate_documents=(
            parse_estate_document("nobles_estate = { color = pop_nobles }\n"),
        ),
        estate_privilege_documents=(
            parse_estate_privilege_document("sample_privilege = { estate = missing_estate }\n"),
        ),
        parliament_agenda_documents=(
            parse_parliament_agenda_document(
                "sample_agenda = {\n"
                "    estate = missing_estate\n"
                "    special_status = elector\n"
                "}\n"
            ),
        ),
        parliament_issue_documents=(
            parse_parliament_issue_document(
                "sample_issue = {\n"
                "    estate = missing_estate\n"
                "    special_status = emperor\n"
                "}\n"
            ),
        ),
    )

    report = catalog.build_report()

    assert report.missing_government_type_references == ("missing_government",)
    assert report.missing_estate_references == ("missing_estate",)
    assert tuple(edge.source_name for edge in report.reform_government_links) == (
        "sample_reform",
    )
    assert tuple(edge.source_name for edge in report.law_government_group_links) == (
        "sample_law",
    )
    assert tuple(edge.source_name for edge in report.privilege_estate_links) == (
        "sample_privilege",
    )
    assert tuple(edge.source_name for edge in report.policy_estate_preference_links) == (
        "policy_a",
    )
