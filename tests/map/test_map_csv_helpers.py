from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.map.map_csv_helpers import (
    parse_map_adjacencies_document,
    parse_map_ports_document,
)
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_map_adjacencies_document_inline() -> None:
    document = parse_map_adjacencies_document(
        "From;To;Type;Through;start_x;start_y;stop_x;stop_y;Comment\n"
        "messina;reggiocal;sea;strait_messina;8396;5518;8404;5519;xxx\n"
    )

    connection = document.get_connection("messina", "reggiocal")
    assert connection is not None
    assert connection.adjacency_type == "sea"
    assert connection.through == "strait_messina"
    assert connection.start_x == 8396
    assert connection.stop_y == 5519
    assert connection.comment == "xxx"


@pytest.mark.timeout(5)
def test_parse_real_map_adjacencies_document(game_install: GameInstall) -> None:
    document = parse_map_adjacencies_document(
        _read_text(game_install.representative_files()["map_adjacencies"])
    )

    connection = document.get_connection("messina", "reggiocal")
    assert connection is not None
    assert connection.adjacency_type == "sea"
    assert connection.through == "strait_messina"
    assert connection.start_x == 8396
    assert connection.start_y == 5518
    assert connection.stop_x == 8404
    assert connection.stop_y == 5519
    assert connection.comment == "xxx"


def test_parse_map_ports_document_inline() -> None:
    document = parse_map_ports_document(
        "LandProvince;SeaZone;x;y;\n"
        "stockholm;stockholms_skargard;8532;6945;x\n"
    )

    port = document.get_port("stockholm")
    assert port is not None
    assert port.sea_zone == "stockholms_skargard"
    assert port.x == 8532
    assert port.y == 6945
    assert port.marker == "x"


@pytest.mark.timeout(5)
def test_parse_real_map_ports_document(game_install: GameInstall) -> None:
    document = parse_map_ports_document(
        _read_text(game_install.representative_files()["map_ports"])
    )

    port = document.get_port("stockholm")
    assert port is not None
    assert port.sea_zone == "stockholms_skargard"
    assert port.x == 8532
    assert port.y == 6945
    assert port.marker == "x"


def test_map_ports_missing_marker_is_none() -> None:
    document = parse_map_ports_document(
        "LandProvince;SeaZone;x;y;\n"
        "stockholm;stockholms_skargard;8532;6945;\n"
    )

    port = document.get_port("stockholm")
    assert port is not None
    assert port.marker is None

