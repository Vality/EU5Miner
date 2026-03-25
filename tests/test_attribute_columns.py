from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.attribute_columns import parse_attribute_column_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_market_attribute_columns(game_install: GameInstall) -> None:
    document = parse_attribute_column_document(
        _read_text(game_install.representative_files()["attribute_column_market_sample"])
    )

    market = document.get_group("market")
    assert market is not None
    assert market.get_column("name") is not None
    assert market.get_column("market_food") is not None

    market_food = market.get_column("market_food")
    assert market_food is not None
    assert market_food.widget == "market_food"
    assert market_food.width == "100"
    assert market_food.fixed_height == "32"
    assert market_food.is_constant_width is True
    assert market_food.sorts[0].sort_value is not None
    assert market_food.sorts[0].sort_by_tooltip_key == '"MARKET_SORT_BY_FOOD"'


@pytest.mark.timeout(5)
def test_parse_real_default_and_secondary_attribute_columns(game_install: GameInstall) -> None:
    default_document = parse_attribute_column_document(
        _read_text(game_install.representative_files()["attribute_column_default_sample"])
    )
    goods_document = parse_attribute_column_document(
        _read_text(game_install.representative_files()["attribute_column_secondary_sample"])
    )

    default_group = default_document.get_group("default")
    assert default_group is not None
    name_column = default_group.get_column("name")
    assert name_column is not None
    assert name_column.widget == "default_text_column"
    assert name_column.is_constant_width is False

    left_click_cost = default_group.get_column("left_click_cost")
    assert left_click_cost is not None
    assert left_click_cost.sorts[0].get_scalar("sort_by_cost_button") == "Left"
    assert left_click_cost.sorts[0].get_scalar("sort_by_cost_type") == "Click"

    goods_group = goods_document.get_group("goods")
    assert goods_group is not None
    goods_name = goods_group.get_column("name")
    assert goods_name is not None
    assert goods_name.sorts[0].sort_text is not None


def test_attribute_columns_parse_inline_fields() -> None:
    document = parse_attribute_column_document(
        "market = {\n"
        "    name = {\n"
        "        widget = default_text_column\n"
        "        width = 150\n"
        "        is_constant_width = no\n"
        "        contains_select_target_button = yes\n"
        "        single_widget_for_row = no\n"
        "        sort = {\n"
        "            sort_by_tooltip_key = \"SORT_TEXT_NAME_TT\"\n"
        "        }\n"
        "    }\n"
        "}\n"
    )

    market = document.get_group("market")
    assert market is not None
    name_column = market.get_column("name")
    assert name_column is not None
    assert name_column.widget == "default_text_column"
    assert name_column.width == "150"
    assert name_column.is_constant_width is False
    assert name_column.contains_select_target_button is True
    assert name_column.single_widget_for_row is False
    assert len(name_column.sorts) == 1
    assert name_column.sorts[0].sort_by_tooltip_key == '"SORT_TEXT_NAME_TT"'
