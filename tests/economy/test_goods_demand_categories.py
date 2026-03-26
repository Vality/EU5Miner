from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.economy.goods_demand_categories import parse_goods_demand_category_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_goods_demand_category_document(game_install: GameInstall) -> None:
    document = parse_goods_demand_category_document(
        _read_text(game_install.representative_files()["goods_demand_category_sample"])
    )

    building_construction = document.get_definition("building_construction")
    assert building_construction is not None
    assert building_construction.display == "integer"

    pop_needs = document.get_definition("pop_needs")
    assert pop_needs is not None
    assert pop_needs.display == "pop"


def test_goods_demand_category_parses_inline_definition() -> None:
    document = parse_goods_demand_category_document("special_demands = { display = integer }\n")

    definition = document.get_definition("special_demands")
    assert definition is not None
    assert definition.display == "integer"

