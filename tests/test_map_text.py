from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.map_text import parse_default_map_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_default_map_document_inline() -> None:
    document = parse_default_map_document(
        'provinces = "locations.png"\n'
        'rivers = "rivers.png"\n'
        'topology = "heightmap.heightmap"\n'
        'adjacencies = "adjacencies.csv"\n'
        'setup = "definitions.txt"\n'
        'ports = "ports.csv"\n'
        'location_templates = "location_templates.txt"\n'
        'equator_y = 3340\n'
        'wrap_x = yes\n'
        'sound_toll = { oresund = helsingor }\n'
        'volcanoes = { klikitat daha }\n'
        'earthquakes = { lisbon naples }\n'
        'sea_zones = { baltic north_sea }\n'
        'lakes = { malaren }\n'
        'impassable_mountains = { skanderna }\n'
        'non_ownable = { sahara_corridor }\n'
    )

    assert document.referenced_files.provinces == '"locations.png"'
    assert document.referenced_files.location_templates == '"location_templates.txt"'
    assert document.equator_y == 3340
    assert document.wrap_x is True
    assert document.get_sound_toll("oresund") is not None
    assert document.get_sound_toll("oresund").location == "helsingor"
    assert document.volcanoes == ("klikitat", "daha")
    assert document.earthquakes == ("lisbon", "naples")
    assert document.sea_zones == ("baltic", "north_sea")
    assert document.lakes == ("malaren",)
    assert document.impassable_mountains == ("skanderna",)
    assert document.non_ownable == ("sahara_corridor",)


@pytest.mark.timeout(5)
def test_parse_real_default_map_document(game_install: GameInstall) -> None:
    document = parse_default_map_document(
        _read_text(game_install.representative_files()["map_default"])
    )

    assert document.referenced_files.provinces == '"locations.png"'
    assert document.referenced_files.adjacencies == '"adjacencies.csv"'
    assert document.referenced_files.location_templates == '"location_templates.txt"'
    assert document.equator_y == 3340
    assert document.wrap_x is True

    oresund = document.get_sound_toll("oresund")
    assert oresund is not None
    assert oresund.location == "helsingor"

    assert "klikitat" in document.volcanoes
    assert "lisbon" in document.earthquakes
    assert "kattegatt" in document.sea_zones
    assert "malaren" in document.lakes
    assert "skanderna" in document.impassable_mountains
    assert "timimoun_qulaia_corridor" in document.non_ownable


def test_missing_default_map_sections_return_empty_or_none() -> None:
    document = parse_default_map_document("wrap_x = no\n")

    assert document.referenced_files.as_dict() == {
        "provinces": None,
        "rivers": None,
        "topology": None,
        "adjacencies": None,
        "setup": None,
        "ports": None,
        "location_templates": None,
    }
    assert document.equator_y is None
    assert document.wrap_x is False
    assert document.sound_tolls == ()
    assert document.volcanoes == ()
    assert document.earthquakes == ()
