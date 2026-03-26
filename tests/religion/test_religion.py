from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.source import ContentPhase
from eu5miner.domains.religion.holy_sites import parse_holy_site_document
from eu5miner.domains.religion import (
    ReligionCatalog,
    ReligionReport,
    build_religion_catalog,
    build_religion_report,
)
from eu5miner.domains.religion.religions import parse_religion_document
from eu5miner.domains.religion.religious_aspects import parse_religious_aspect_document
from eu5miner.domains.religion.religious_factions import parse_religious_faction_document
from eu5miner.domains.religion.religious_figures import parse_religious_figure_document
from eu5miner.domains.religion.religious_focuses import parse_religious_focus_document
from eu5miner.domains.religion.religious_schools import parse_religious_school_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_build_religion_catalog_links_real_family_definitions(
    game_install: GameInstall,
) -> None:
    catalog = build_religion_catalog(
        religion_documents=(
            parse_religion_document(_read_text(game_install.representative_files()["religion_sample"])),
            parse_religion_document(
                _read_text(game_install.representative_files()["religion_secondary_sample"])
            ),
            parse_religion_document(
                _read_text(game_install.representative_files()["religion_muslim_sample"])
            ),
            parse_religion_document(
                _read_text(game_install.representative_files()["religion_tonal_sample"])
            ),
            parse_religion_document(
                _read_text(game_install.representative_files()["religion_dharmic_sample"])
            ),
        ),
        religious_aspect_documents=(
            parse_religious_aspect_document(
                _read_text(game_install.representative_files()["religious_aspect_sample"])
            ),
        ),
        religious_faction_documents=(
            parse_religious_faction_document(
                _read_text(game_install.representative_files()["religious_faction_sample"])
            ),
        ),
        religious_focus_documents=(
            parse_religious_focus_document(
                _read_text(game_install.representative_files()["religious_focus_sample"])
            ),
        ),
        religious_school_documents=tuple(
            parse_religious_school_document(_read_text(path))
            for path in game_install.iter_phase_files(
                ContentPhase.IN_GAME,
                "common/religious_schools",
            )
        ),
        religious_figure_documents=(
            parse_religious_figure_document(
                _read_text(game_install.representative_files()["religious_figure_sample"])
            ),
            parse_religious_figure_document(
                _read_text(game_install.representative_files()["religious_figure_secondary_sample"])
            ),
        ),
        holy_site_documents=(
            parse_holy_site_document(_read_text(game_install.representative_files()["holy_site_sample"])),
            parse_holy_site_document(
                _read_text(game_install.representative_files()["holy_site_secondary_sample"])
            ),
        ),
    )

    assert "adult_baptism" in {
        definition.name for definition in catalog.get_religious_aspects_for_religion("anglican")
    }
    assert "imperial_court" in {
        definition.name for definition in catalog.get_religious_factions_for_religion("shinto")
    }
    assert "adopt_ometeotl" in {
        definition.name for definition in catalog.get_religious_focuses_for_religion("nahuatl")
    }
    assert "hanafi_school" in {
        definition.name for definition in catalog.get_religious_schools_for_religion("sunni")
    }
    assert "yoga_school" in {
        definition.name for definition in catalog.get_religious_schools_for_religion("hindu")
    }
    assert "muslim_scholar" in {
        definition.name for definition in catalog.get_religious_figures_for_religion("sunni")
    }
    assert "guru" in {
        definition.name for definition in catalog.get_religious_figures_for_religion("hindu")
    }
    assert "jerusalem_the_holy_city_catholic" in {
        definition.name for definition in catalog.get_holy_sites_for_religion("catholic")
    }
    assert "varanasi_holy_city" in {
        definition.name for definition in catalog.get_holy_sites_for_religion("hindu")
    }

    report = build_religion_report(catalog)
    assert report.missing_religious_faction_references == ()
    assert report.missing_religious_focus_references == ()
    assert report.missing_religious_school_references == ()
    assert isinstance(catalog, ReligionCatalog)
    assert isinstance(report, ReligionReport)


def test_build_religion_report_collects_missing_explicit_references() -> None:
    catalog = build_religion_catalog(
        religion_documents=(
            parse_religion_document(
                "faith = {\n"
                "    group = christian\n"
                "    factions = { missing_faction }\n"
                "    religious_focuses = { missing_focus }\n"
                "    religious_school = missing_school\n"
                "}\n"
            ),
        ),
        religious_aspect_documents=(
            parse_religious_aspect_document("sample_aspect = { religion = faith }\n"),
        ),
        religious_figure_documents=(
            parse_religious_figure_document(
                "sample_figure = { enabled_for_religion = { group = religion_group:christian } }\n"
            ),
        ),
        holy_site_documents=(
            parse_holy_site_document(
                "sample_site = {\n"
                "    location = rome\n"
                "    religions = {\n"
                "        faith\n"
                "    }\n"
                "}\n"
            ),
        ),
    )

    assert tuple(definition.name for definition in catalog.get_religious_aspects_for_religion("faith")) == (
        "sample_aspect",
    )
    assert tuple(definition.name for definition in catalog.get_religious_figures_for_religion("faith")) == (
        "sample_figure",
    )
    assert tuple(definition.name for definition in catalog.get_holy_sites_for_religion("faith")) == (
        "sample_site",
    )

    report = catalog.build_report()
    assert report.missing_religious_faction_references == ("missing_faction",)
    assert report.missing_religious_focus_references == ("missing_focus",)
    assert report.missing_religious_school_references == ("missing_school",)
