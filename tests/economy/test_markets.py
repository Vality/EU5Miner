from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.attribute_columns import parse_attribute_column_document
from eu5miner.domains.diplomacy.generic_actions import parse_generic_action_document
from eu5miner.domains.economy import (
    MarketCatalog,
    MarketReport,
    build_market_catalog,
    build_market_report,
)
from eu5miner.domains.economy.goods import parse_goods_document
from eu5miner.domains.economy.prices import parse_price_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_build_market_catalog_collects_market_helpers() -> None:
    goods_document = parse_goods_document(
        "iron = {\n"
        "    method = mining\n"
        "    category = raw_material\n"
        "    default_market_price = 3\n"
        "}\n"
        "wood = {\n"
        "    method = logging\n"
        "    category = raw_material\n"
        "}\n"
    )
    price_document = parse_price_document("build_road = { gold = 10 }\n")
    generic_action_document = parse_generic_action_document(
        "create_market = {\n"
        "    type = owncountry\n"
        "    select_trigger = { looking_for_a = market }\n"
        "}\n"
        "create_building = {\n"
        "    type = owncountry\n"
        "    select_trigger = { looking_for_a = building }\n"
        "}\n"
    )
    attribute_column_document = parse_attribute_column_document(
        "market = { name = { widget = default_text_column } }\n"
        "goods = { price = { widget = default_numeric_column } }\n"
    )

    catalog = build_market_catalog(
        goods_documents=(goods_document,),
        price_documents=(price_document,),
        generic_action_documents=(generic_action_document,),
        attribute_column_documents=(attribute_column_document,),
    )
    report = build_market_report(catalog)

    assert catalog.get_good("iron") is not None
    assert catalog.get_price("build_road") is not None
    assert catalog.get_generic_action("create_market") is not None
    assert catalog.get_attribute_group("market") is not None
    assert tuple(definition.name for definition in catalog.get_market_actions()) == (
        "create_market",
    )
    assert tuple(
        definition.name for definition in catalog.get_goods_with_default_market_price()
    ) == ("iron",)
    assert tuple(definition.name for definition in catalog.get_columns_for_group("market")) == (
        "name",
    )
    assert report.available_attribute_groups == ("goods", "market")
    assert report.priced_goods == ("iron",)
    assert report.action_target_links[0].source_name == "create_market"
    assert report.action_target_links[0].referenced_names == ("market",)
    assert isinstance(catalog, MarketCatalog)
    assert isinstance(report, MarketReport)


@pytest.mark.timeout(5)
def test_build_market_catalog_with_real_market_samples(game_install: GameInstall) -> None:
    representative_files = game_install.representative_files()
    goods_document = parse_goods_document(_read_text(representative_files["goods_sample"]))
    price_document = parse_price_document(_read_text(representative_files["price_sample"]))
    generic_action_document = parse_generic_action_document(
        _read_text(representative_files["generic_action_market_sample"])
    )
    attribute_column_document = parse_attribute_column_document(
        _read_text(representative_files["attribute_column_market_sample"])
    )

    catalog = build_market_catalog(
        goods_documents=(goods_document,),
        price_documents=(price_document,),
        generic_action_documents=(generic_action_document,),
        attribute_column_documents=(attribute_column_document,),
    )
    report = catalog.build_report()

    assert catalog.get_good("horses") is not None
    assert len(catalog.price_definitions) > 0
    assert catalog.get_attribute_group("market") is not None
    assert len(catalog.get_market_actions()) > 0
    assert "market" in report.available_attribute_groups
    assert "horses" in report.priced_goods
