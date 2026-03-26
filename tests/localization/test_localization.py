from __future__ import annotations

from pathlib import Path

from eu5miner.formats.localization import parse_localization
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def test_parse_real_localization_file(game_install: GameInstall) -> None:
    localization = parse_localization(
        _read_text(game_install.representative_files()["localization_sample"])
    )

    assert localization.language == "l_english"
    assert len(localization.entries) > 10
    assert any(entry.key == "ACTION_COST" for entry in localization.entries)


def test_parse_small_localization_sample() -> None:
    sample = 'l_english:\n test_key: "Hello"\n next_key: "World"\n'
    localization = parse_localization(sample)

    assert localization.language == "l_english"
    assert [entry.key for entry in localization.entries] == ["test_key", "next_key"]
