from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.country_description_categories import (
    build_country_description_category_usage_document,
    parse_country_description_category_document,
)
from eu5miner.domains.map.setup_countries import parse_setup_country_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_country_description_category_document(
    game_install: GameInstall,
) -> None:
    document = parse_country_description_category_document(
        _read_text(game_install.representative_files()["country_description_category_sample"])
    )

    assert document.names() == ("diplomatic", "administrative", "military")
    assert document.get_definition("military") is not None


@pytest.mark.timeout(5)
def test_build_real_country_description_category_usage_document(
    game_install: GameInstall,
) -> None:
    category_document = parse_country_description_category_document(
        _read_text(game_install.representative_files()["country_description_category_sample"])
    )
    setup_document = parse_setup_country_document(
        _read_text(game_install.representative_files()["setup_country_sample"])
    )

    usage_document = build_country_description_category_usage_document(
        category_document,
        setup_document,
    )

    assert "military" in usage_document.names()

    military_usage = usage_document.get_usage("military")
    assert military_usage is not None
    assert military_usage.is_defined is True
    assert "FRA" in military_usage.country_tags

    france = usage_document.get_assignment("FRA")
    assert france is not None
    assert france.category_name == "military"
    assert france.is_defined is True


def test_build_country_description_category_usage_document_tracks_unknown_categories() -> None:
    category_document = parse_country_description_category_document(
        "military = {}\n"
        "administrative = {}\n"
    )
    setup_document = parse_setup_country_document(
        "AAA = { description_category = military }\n"
        "BBB = { description_category = maritime }\n"
    )

    usage_document = build_country_description_category_usage_document(
        category_document,
        setup_document,
    )

    assert usage_document.names() == ("administrative", "maritime", "military")

    military_usage = usage_document.get_usage("military")
    assert military_usage is not None
    assert military_usage.country_tags == ("AAA",)

    maritime_usage = usage_document.get_usage("maritime")
    assert maritime_usage is not None
    assert maritime_usage.is_defined is False
    assert maritime_usage.country_tags == ("BBB",)

    bbb = usage_document.get_assignment("BBB")
    assert bbb is not None
    assert bbb.category is None
    assert bbb.is_defined is False

