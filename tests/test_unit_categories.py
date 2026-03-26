from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.unit_categories import parse_unit_category_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_unit_category_document(game_install: GameInstall) -> None:
    document = parse_unit_category_document(
        _read_text(game_install.representative_files()["unit_category_sample"])
    )

    definition = document.get_definition("army_infantry")
    assert definition is not None
    assert definition.is_army is True
    assert definition.assault is True
    assert definition.is_garrison is True
    assert definition.build_time == "standard_inf_recruitment_time"
    assert definition.startup_amount == 20
    assert definition.ai_weight == 0.5
    assert definition.get_modifier("movement_speed") == "2.5"
    assert definition.get_modifier("damage_taken") == "1.0"


@pytest.mark.timeout(5)
def test_parse_real_variant_unit_category_document(game_install: GameInstall) -> None:
    document = parse_unit_category_document(
        _read_text(game_install.representative_files()["unit_category_secondary_sample"])
    )

    definition = document.get_definition("navy_transport")
    assert definition is not None
    assert definition.is_army is False
    assert definition.transport is True
    assert definition.build_time == "transport_build_time"
    assert definition.get_modifier("transport_capacity") == "0.2"
    assert definition.get_modifier("anti_piracy_warfare") == "0.05"


def test_unit_category_parses_inline_variant_fields() -> None:
    document = parse_unit_category_document(
        "sample_category = {\n"
        "    startup_amount = 1\n"
        "    bombard = yes\n"
        "    auxiliary = yes\n"
        "    combat = { open_sea = 0.2 }\n"
        "    attrition_loss = 0.25\n"
        "}\n"
    )

    definition = document.get_definition("sample_category")
    assert definition is not None
    assert definition.startup_amount == 1
    assert definition.bombard is True
    assert definition.auxiliary is True
    assert definition.combat is not None
    assert definition.get_modifier("attrition_loss") == "0.25"
