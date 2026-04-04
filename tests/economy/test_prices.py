from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.economy.prices import parse_price_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_price_document(game_install: GameInstall) -> None:
    document = parse_price_document(_read_text(game_install.representative_files()["price_sample"]))

    build_railroad = document.get_definition("build_railroad")
    assert build_railroad is not None
    assert build_railroad.gold == "100"

    send_gift = document.get_definition("send_gift")
    assert send_gift is not None
    assert send_gift.scaled_recipient_gold == "2"
    assert send_gift.scaled_gold == "1"
    assert send_gift.min_scale == "25"


@pytest.mark.timeout(5)
def test_parse_secondary_real_price_document(game_install: GameInstall) -> None:
    document = parse_price_document(
        _read_text(game_install.representative_files()["price_secondary_sample"])
    )

    city_upgrade = document.get_definition("city_upgrade")
    assert city_upgrade is not None
    assert city_upgrade.gold == "2000"

    remove_panaqa_early = document.get_definition("remove_panaqa_early")
    assert remove_panaqa_early is not None
    assert remove_panaqa_early.legitimacy == "10"


def test_price_parses_inline_fields() -> None:
    document = parse_price_document(
        "sample_price = {\n"
        "    scaled_gold = 2.5\n"
        "    prestige = 10\n"
        "    min_scale = 5\n"
        "    max_scale = 100\n"
        "}\n"
    )

    definition = document.get_definition("sample_price")
    assert definition is not None
    assert definition.scaled_gold == "2.5"
    assert definition.prestige == "10"
    assert definition.min_scale == "5"
    assert definition.max_scale == "100"
