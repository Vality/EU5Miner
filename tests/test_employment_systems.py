from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.employment_systems import parse_employment_system_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_employment_system_document(game_install: GameInstall) -> None:
    document = parse_employment_system_document(
        _read_text(game_install.representative_files()["employment_system_sample"])
    )

    equality = document.get_definition("equality")
    assert equality is not None
    assert equality.country_modifier is not None
    assert equality.priority is not None
    assert equality.ai_will_do is not None

    capitalism = document.get_definition("capitalism")
    assert capitalism is not None
    assert capitalism.priority is not None
    assert capitalism.priority.get_scalar("value") == "building_potential_profit"


def test_employment_system_parses_inline_fields() -> None:
    document = parse_employment_system_document(
        "sample_system = {\n"
        "    country_modifier = { monthly_towards_communalism = 1 }\n"
        "    priority = { value = 10 }\n"
        "    ai_will_do = { add = { value = 5 } }\n"
        "}\n"
    )

    definition = document.get_definition("sample_system")
    assert definition is not None
    assert definition.country_modifier is not None
    assert definition.priority is not None
    assert definition.ai_will_do is not None
