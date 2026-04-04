from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.economy.goods import parse_goods_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_goods_document(game_install: GameInstall) -> None:
    document = parse_goods_document(_read_text(game_install.representative_files()["goods_sample"]))

    horses = document.get_definition("horses")
    assert horses is not None
    assert horses.method == "farming"
    assert horses.category == "raw_material"
    assert horses.color == "goods_horses"
    assert horses.default_market_price == "3"
    assert horses.transport_cost == "2"
    assert horses.origin_in_old_world is True
    assert horses.custom_tags == ("old_world_goods",)
    assert horses.demand_add[0].name == "nobles"
    assert horses.demand_add[0].amount == "0.25"


@pytest.mark.timeout(5)
def test_parse_secondary_real_goods_document(game_install: GameInstall) -> None:
    document = parse_goods_document(
        _read_text(game_install.representative_files()["goods_secondary_sample"])
    )

    wheat = document.get_definition("wheat")
    assert wheat is not None
    assert wheat.food == "8.0"
    assert wheat.origin_in_old_world is True
    assert wheat.custom_tags == ("old_world_goods",)
    assert wheat.wealth_impact_threshold[0].name == "peasants"
    assert wheat.wealth_impact_threshold[0].amount == "1.1"


def test_goods_parses_inline_fields() -> None:
    document = parse_goods_document(
        "iron = {\n"
        "    method = mining\n"
        "    category = raw_material\n"
        "    default_market_price = 3\n"
        "    origin_in_new_world = yes\n"
        "    demand_add = { all = 0.2 }\n"
        "    custom_tags = { strategic }\n"
        "}\n"
    )

    definition = document.get_definition("iron")
    assert definition is not None
    assert definition.method == "mining"
    assert definition.origin_in_new_world is True
    assert definition.demand_add[0].name == "all"
    assert definition.custom_tags == ("strategic",)
