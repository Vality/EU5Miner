from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.holy_site_types import parse_holy_site_type_document
from eu5miner.domains.holy_sites import (
    HolySiteCatalog,
    HolySiteReport,
    build_holy_site_catalog,
    build_holy_site_report,
    parse_holy_site_document,
)
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_holy_site_documents_and_catalog(game_install: GameInstall) -> None:
    type_document = parse_holy_site_type_document(
        _read_text(game_install.representative_files()["holy_site_type_sample"])
    )
    catholic = parse_holy_site_document(
        _read_text(game_install.representative_files()["holy_site_sample"])
    )
    hindu = parse_holy_site_document(
        _read_text(game_install.representative_files()["holy_site_secondary_sample"])
    )

    jerusalem = catholic.get_definition("jerusalem_the_holy_city_catholic")
    assert jerusalem is not None
    assert jerusalem.location == "jerusalem"
    assert jerusalem.holy_site_type == "christian_holy_site"
    assert jerusalem.importance == 5
    assert "catholic" in jerusalem.religions

    ranganatha = hindu.get_definition("ranganathaswamy_temple")
    assert ranganatha is not None
    assert ranganatha.holy_site_type == "temple"
    assert ranganatha.god == "vishnu_god"

    matsya = hindu.get_definition("matsya_narayana")
    assert matsya is not None
    assert matsya.avatar == "matsya_avatar"

    catalog = build_holy_site_catalog((type_document,), (catholic, hindu))
    assert tuple(site.name for site in catalog.get_holy_sites_for_type("christian_holy_site")) == (
        "jerusalem_the_holy_city_catholic",
        "the_vatican",
        "santiago_de_compostela_cathedral",
        "chartres_cathedral",
        "cologne_cathedral",
        "canterbury_cathedral",
    )
    assert "varanasi_holy_city" in {
        site.name for site in catalog.get_holy_sites_for_religion("hindu")
    }
    assert "ranganathaswamy_temple" in {
        site.name for site in catalog.get_holy_sites_for_god("vishnu_god")
    }
    assert "matsya_narayana" in {
        site.name for site in catalog.get_holy_sites_for_avatar("matsya_avatar")
    }

    report = build_holy_site_report(catalog)
    assert report.missing_holy_site_type_references == ()
    assert isinstance(catalog, HolySiteCatalog)
    assert isinstance(report, HolySiteReport)


def test_holy_site_parses_inline_variant_fields_and_missing_type_report() -> None:
    type_document = parse_holy_site_type_document("temple = { location_modifier = { add = 1 } }\n")
    site_document = parse_holy_site_document(
        "sample_site = {\n"
        "    location = rome\n"
        "    type = temple\n"
        "    importance = 4\n"
        "    religions = { catholic orthodox }\n"
        "    god = saint_peter\n"
        "    avatar = martyr_avatar\n"
        "}\n"
        "missing_site = {\n"
        "    location = paris\n"
        "    type = missing_type\n"
        "    importance = 2\n"
        "    religions = { catholic }\n"
        "}\n"
    )

    sample = site_document.get_definition("sample_site")
    assert sample is not None
    assert sample.location == "rome"
    assert sample.holy_site_type == "temple"
    assert sample.importance == 4
    assert sample.religions == ("catholic", "orthodox")
    assert sample.god == "saint_peter"
    assert sample.avatar == "martyr_avatar"

    catalog = build_holy_site_catalog((type_document,), (site_document,))
    report = catalog.build_report()
    assert report.missing_holy_site_type_references == ("missing_type",)
