from __future__ import annotations

from pathlib import Path

from eu5miner.formats.metadata import parse_metadata_json
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_real_dlc_metadata(game_install: GameInstall) -> None:
    metadata = parse_metadata_json(_read_text(game_install.representative_files()["dlc_metadata"]))

    assert metadata["name"] == "Shared DLC Data"
    assert metadata["path"] == "dlc/D000_shared"
    assert isinstance(metadata["dependencies"], list)


def test_metadata_requires_object() -> None:
    try:
        parse_metadata_json("[]")
    except ValueError as exc:
        assert "object" in str(exc)
    else:
        raise AssertionError("Expected metadata parser to reject non-object JSON")
