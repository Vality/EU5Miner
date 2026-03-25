from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.script_values import parse_script_value_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_script_value_formula_document(game_install: GameInstall) -> None:
    document = parse_script_value_document(
        _read_text(game_install.representative_files()["script_value_sample"])
    )

    assert document.names() == ("best_capital_for_colony",)

    definition = document.get_definition("best_capital_for_colony")
    assert definition is not None
    assert definition.is_formula is True
    assert definition.is_scalar is False
    assert definition.formula is not None
    assert definition.formula.get_scalar("value") == "population"


@pytest.mark.timeout(5)
def test_parse_real_script_value_scalar_document(game_install: GameInstall) -> None:
    document = parse_script_value_document(
        _read_text(game_install.representative_files()["script_value_scalar_sample"])
    )

    assert len(document.definitions) > 20
    assert document.definitions[0].name == "tech_level_to_advances_1"

    definition = document.get_definition("tech_level_to_advances_10")
    assert definition is not None
    assert definition.is_scalar is True
    assert definition.is_formula is False
    assert definition.scalar_text == "45"
    assert definition.parameters == ()


def test_script_value_formula_parameters_are_detected() -> None:
    document = parse_script_value_document(
        "my_script_value = {\n"
        "    value = $base$\n"
        "    add = $bonus$\n"
        "    $target$ = { value = $nested$ }\n"
        "}\n"
    )

    definition = document.get_definition("my_script_value")
    assert definition is not None
    assert definition.parameters == ("base", "bonus", "nested", "target")
    assert definition.formula is not None


def test_script_value_scalar_definition_keeps_scalar_text() -> None:
    document = parse_script_value_document("minor_stress_gain = 10\n")

    definition = document.get_definition("minor_stress_gain")
    assert definition is not None
    assert definition.is_scalar is True
    assert definition.scalar_text == "10"
    assert definition.formula is None
