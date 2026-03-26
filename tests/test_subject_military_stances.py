from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.subject_military_stances import parse_subject_military_stance_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_subject_military_stance_document(game_install: GameInstall) -> None:
    document = parse_subject_military_stance_document(
        _read_text(game_install.representative_files()["subject_military_stance_sample"])
    )

    assert document.names() == (
        "normal_military_stance",
        "aggressive_military_stance",
        "supportive_military_stance",
        "passive_military_stance",
        "defensive_military_stance",
    )

    normal = document.get_definition("normal_military_stance")
    assert normal is not None
    assert normal.is_default is True
    assert normal.chase_unit_own_location_priority == 10.0
    assert normal.support_sieges_priority is None

    aggressive = document.get_definition("aggressive_military_stance")
    assert aggressive is not None
    assert aggressive.support_sieges_priority == 0.0
    assert aggressive.hunt_army_priority == 8.0


def test_subject_military_stance_parses_inline_fields() -> None:
    document = parse_subject_military_stance_document(
        "sample_military_stance = {\n"
        "    is_default = no\n"
        "    chase_navy_priority = 4.5\n"
        "    support_sieges_priority = 2\n"
        "}\n"
    )

    definition = document.get_definition("sample_military_stance")
    assert definition is not None
    assert definition.is_default is False
    assert definition.chase_navy_priority == 4.5
    assert definition.support_sieges_priority == 2.0
