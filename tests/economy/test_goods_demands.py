from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.economy.goods_demands import parse_goods_demand_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_goods_demand_document(game_install: GameInstall) -> None:
    document = parse_goods_demand_document(
        _read_text(game_install.representative_files()["goods_demand_sample"])
    )

    horse_breeders = document.get_definition("horse_breeders_construction")
    assert horse_breeders is not None
    assert horse_breeders.category == "building_construction"
    assert horse_breeders.hidden is None
    assert horse_breeders.scalar_demands[0].name == "masonry"
    assert horse_breeders.scalar_demands[0].amount == "0.5"


@pytest.mark.timeout(5)
def test_parse_scripted_real_goods_demand_document(game_install: GameInstall) -> None:
    document = parse_goods_demand_document(
        _read_text(game_install.representative_files()["goods_demand_secondary_sample"])
    )

    pop_demand = document.get_definition("pop_demand")
    assert pop_demand is not None
    assert pop_demand.category == "pop_needs"
    assert len(pop_demand.scripted_demands) > 3
    assert pop_demand.scripted_demands[0].name == "wine"
    assert pop_demand.scripted_demands[0].body.get_scalar("value") == "1"


@pytest.mark.timeout(5)
def test_parse_hidden_goods_demand_document(game_install: GameInstall) -> None:
    document = parse_goods_demand_document(
        _read_text(game_install.representative_files()["goods_demand_tertiary_sample"])
    )

    silver_fancy = document.get_definition("silver_fancy")
    assert silver_fancy is not None
    assert silver_fancy.hidden is True
    assert silver_fancy.category == "special_demands"
    assert silver_fancy.scalar_demands[0].name == "silver"
    assert silver_fancy.scalar_demands[0].amount == "20"


def test_goods_demand_parses_inline_fields() -> None:
    document = parse_goods_demand_document(
        "sample_demand = {\n"
        "    iron = 0.5\n"
        "    category = ship_construction\n"
        "    hidden = yes\n"
        "    wine = { value = 1 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_demand")
    assert definition is not None
    assert definition.category == "ship_construction"
    assert definition.hidden is True
    assert definition.scalar_demands[0].name == "iron"
    assert definition.scripted_demands[0].name == "wine"
