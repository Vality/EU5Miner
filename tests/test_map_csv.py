from __future__ import annotations

from pathlib import Path

from eu5miner.formats.map_csv import parse_semicolon_csv
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_real_adjacency_csv(game_install: GameInstall) -> None:
    rows = parse_semicolon_csv(_read_text(game_install.representative_files()["map_adjacencies"]))

    assert rows
    assert rows[0]["From"] == "messina"
    assert rows[0]["Type"] == "sea"


def test_parse_small_semicolon_csv() -> None:
    rows = parse_semicolon_csv("From;To\na;b\n")

    assert rows == [{"From": "a", "To": "b"}]
