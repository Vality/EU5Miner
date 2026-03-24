from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.scripted_triggers import parse_scripted_trigger_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_scripted_trigger_document(game_install: GameInstall) -> None:
    document = parse_scripted_trigger_document(
        _read_text(game_install.representative_files()["scripted_trigger"])
    )

    assert len(document.definitions) > 5
    assert document.definitions[0].name == "country_can_ennoble_trigger"
    assert document.get_definition("country_rank_is_what") is not None


def test_scripted_trigger_parameters_are_detected() -> None:
    document = parse_scripted_trigger_document(
        "my_argument_trigger = {\n"
        "    prestige = $value$\n"
        "    $target$ = { prestige = $value$ }\n"
        "}\n"
    )

    definition = document.get_definition("my_argument_trigger")
    assert definition is not None
    assert definition.parameters == ("target", "value")


def test_real_trigger_with_arguments_reports_parameter_names(game_install: GameInstall) -> None:
    document = parse_scripted_trigger_document(
        _read_text(game_install.representative_files()["scripted_trigger"])
    )

    definition = document.get_definition("country_rank_is_what")
    assert definition is not None
    assert "target_rank" in definition.parameters
