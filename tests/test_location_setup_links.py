from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.location_setup_links import (
    build_linked_location_document,
    parse_country_location_document,
    parse_location_hierarchy_document,
    parse_location_setup_document,
)
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_location_hierarchy_document_inline() -> None:
    document = parse_location_hierarchy_document(
        "world = {\n"
        "    region = {\n"
        "        area = {\n"
        "            province = { stockholm uppsala }\n"
        "        }\n"
        "    }\n"
        "}\n"
    )

    stockholm = document.get_location("stockholm")
    assert stockholm is not None
    assert stockholm.hierarchy_path == ("world", "region", "area", "province")
    assert stockholm.leaf_group == "province"
    assert document.get_definition("stockholm") == stockholm


def test_parse_country_location_document_inline() -> None:
    document = parse_country_location_document(
        "countries = {\n"
        "    countries = {\n"
        "        SWE = {\n"
        "            own_control_core = { stockholm uppsala }\n"
        "            capital = stockholm\n"
        "        }\n"
        "    }\n"
        "}\n"
    )

    swe = document.get_definition("SWE")
    assert swe is not None
    assert swe.capital == "stockholm"
    assert swe.get_locations("own_control_core") == ("stockholm", "uppsala")


def test_parse_location_setup_document_inline() -> None:
    document = parse_location_setup_document(
        "locations = {\n"
        "    malmo = { timed_modifiers = { } }\n"
        "}\n"
    )

    assert document.get_definition("malmo") is not None


@pytest.mark.timeout(5)
def test_parse_real_location_hierarchy_document(game_install: GameInstall) -> None:
    document = parse_location_hierarchy_document(
        _read_text(game_install.representative_files()["map_definitions"])
    )

    stockholm = document.get_location("stockholm")
    assert stockholm is not None
    assert stockholm.leaf_group == "uppland_province"
    assert stockholm.hierarchy_path[:3] == (
        "europe",
        "western_europe",
        "scandinavian_region",
    )
    assert document.get_definition("stockholm") == stockholm


@pytest.mark.timeout(5)
def test_parse_real_country_location_document(game_install: GameInstall) -> None:
    document = parse_country_location_document(
        _read_text(game_install.representative_files()["main_menu_country_setup_sample"])
    )

    swe = document.get_definition("SWE")
    assert swe is not None
    assert swe.capital == "stockholm"
    assert "stockholm" in swe.get_locations("own_control_core")


@pytest.mark.timeout(5)
def test_build_real_linked_location_document(game_install: GameInstall) -> None:
    hierarchy = parse_location_hierarchy_document(
        _read_text(game_install.representative_files()["map_definitions"])
    )
    country_document = parse_country_location_document(
        _read_text(game_install.representative_files()["main_menu_country_setup_sample"])
    )
    setup_document = parse_location_setup_document(
        _read_text(game_install.representative_files()["main_menu_location_setup_sample"])
    )

    linked = build_linked_location_document(hierarchy, country_document, setup_document)

    stockholm = linked.get_location("stockholm")
    assert stockholm is not None
    assert stockholm.hierarchy is not None
    assert stockholm.hierarchy.leaf_group == "uppland_province"
    assert "SWE" in stockholm.capital_of
    assert any(
        reference.country_tag == "SWE" and reference.category == "own_control_core"
        for reference in stockholm.country_references
    )
    assert stockholm.has_location_setup is False
    assert linked.get_definition("stockholm") == stockholm

    malmo = linked.get_location("malmo")
    assert malmo is not None
    assert malmo.hierarchy is not None
    assert malmo.location_setup is not None
    assert linked.get_definition("malmo") == malmo
