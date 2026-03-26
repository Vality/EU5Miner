from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.economy.production_methods import parse_production_method_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_production_method_document(game_install: GameInstall) -> None:
    document = parse_production_method_document(
        _read_text(game_install.representative_files()["production_method_sample"])
    )

    monastery = document.get_definition("monastery_maintenance")
    assert monastery is not None
    assert monastery.category == "building_maintenance"
    assert monastery.inputs[0].goods == "glass"
    assert monastery.inputs[0].amount == "0.025"
    assert monastery.inputs[-1].goods == "beeswax"

    preacher = document.get_definition("lutheran_preacher_maintenance")
    assert preacher is not None
    assert preacher.no_upkeep is True

    reformed_monastery = document.get_definition("hab_reformed_monastery_maintenance")
    assert reformed_monastery is not None
    assert reformed_monastery.potential is not None


def test_production_method_parses_inline_fields() -> None:
    document = parse_production_method_document(
        "sample_method = {\n"
        "    tools = 0.2\n"
        "    produced = weaponry\n"
        "    output = 1.5\n"
        "    category = building_maintenance\n"
        "    no_upkeep = yes\n"
        "    allow = { has_reform = yes }\n"
        "}\n"
    )

    definition = document.get_definition("sample_method")
    assert definition is not None
    assert definition.inputs == (
        definition.inputs[0],
    )
    assert definition.inputs[0].goods == "tools"
    assert definition.inputs[0].amount == "0.2"
    assert definition.produced == "weaponry"
    assert definition.output == "1.5"
    assert definition.category == "building_maintenance"
    assert definition.no_upkeep is True
    assert definition.allow is not None

