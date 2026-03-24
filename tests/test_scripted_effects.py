from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.scripted_effects import parse_scripted_effect_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_scripted_effect_document(game_install: GameInstall) -> None:
    document = parse_scripted_effect_document(
        _read_text(game_install.representative_files()["scripted_effect"])
    )

    assert len(document.definitions) > 10
    assert document.definitions[0].name == "create_newborn_ruler_child"
    assert document.get_definition("unlock_advance_effect") is not None


def test_scripted_effect_parameters_are_detected() -> None:
    document = parse_scripted_effect_document(
        "my_argument_effect = {\n"
        "    add_prestige = $value$\n"
        "    $target$ = { add_stability = $bonus$ }\n"
        "}\n"
    )

    definition = document.get_definition("my_argument_effect")
    assert definition is not None
    assert definition.parameters == ("bonus", "target", "value")


def test_real_effect_with_arguments_reports_parameter_names(game_install: GameInstall) -> None:
    document = parse_scripted_effect_document(
        _read_text(game_install.representative_files()["scripted_effect"])
    )

    definition = document.get_definition("unlock_advance_effect")
    assert definition is not None
    assert "type" in definition.parameters
