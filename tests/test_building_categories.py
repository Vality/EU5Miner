from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.building_categories import parse_building_category_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_building_category_document(game_install: GameInstall) -> None:
    document = parse_building_category_document(
        _read_text(game_install.representative_files()["building_category_sample"])
    )

    assert "infrastructure_category" in document.names()
    assert "defense_category" in document.names()

    definition = document.get_definition("government_category")
    assert definition is not None
    assert definition.body.entries == ()


def test_building_category_parses_inline_definition() -> None:
    document = parse_building_category_document("trade_category = {}\n")

    definition = document.get_definition("trade_category")
    assert definition is not None
    assert definition.name == "trade_category"
