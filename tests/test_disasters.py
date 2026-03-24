from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.disasters import parse_disaster_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_disaster_document(game_install: GameInstall) -> None:
    document = parse_disaster_document(
        _read_text(game_install.representative_files()["disaster_sample"])
    )

    assert document.names() == ("english_civil_war",)

    definition = document.get_definition("english_civil_war")
    assert definition is not None
    assert definition.image == "gfx/interface/illustrations/disaster/english_civil_war.dds"
    assert definition.monthly_spawn_chance is None
    assert definition.monthly_spawn_chance_object is not None
    assert definition.can_start is not None
    assert definition.can_end is not None
    assert definition.modifier is not None
    assert definition.on_start is not None
    assert definition.on_end is not None
    assert definition.on_monthly is not None


def test_parse_disaster_document_with_scalar_spawn_and_end_trigger() -> None:
    document = parse_disaster_document(
        "sample_disaster = {\n"
        "    image = gfx/interface/illustrations/disaster/sample.dds\n"
        "    monthly_spawn_chance = monthly_spawn_chance_low\n"
        "    sample_disaster_end_trigger = yes\n"
        "    can_start = { always = yes }\n"
        "    can_end = { sample_disaster_end_trigger = yes }\n"
        "    modifier = { monthly_war_exhaustion = 0.1 }\n"
        "    on_start = { set_variable = started_sample_disaster }\n"
        "    on_end = { remove_variable = started_sample_disaster }\n"
        "    on_monthly = { custom_tooltip = sample_disaster_tick_tt }\n"
        "}\n"
    )

    definition = document.get_definition("sample_disaster")
    assert definition is not None
    assert definition.image == "gfx/interface/illustrations/disaster/sample.dds"
    assert definition.monthly_spawn_chance == "monthly_spawn_chance_low"
    assert definition.end_trigger_flags == ("sample_disaster_end_trigger",)
    assert definition.can_start is not None
    assert definition.can_end is not None
    assert definition.modifier is not None
    assert definition.on_start is not None
    assert definition.on_end is not None
    assert definition.on_monthly is not None


def test_parse_disaster_document_with_object_spawn_chance() -> None:
    document = parse_disaster_document(
        "complex_disaster = {\n"
        "    monthly_spawn_chance = {\n"
        "        value = monthly_spawn_chance_low\n"
        "        add = monthly_spawn_chance_very_low\n"
        "    }\n"
        "    can_start = { always = yes }\n"
        "}\n"
    )

    definition = document.get_definition("complex_disaster")
    assert definition is not None
    assert definition.monthly_spawn_chance is None
    assert definition.monthly_spawn_chance_object is not None
    assert definition.can_start is not None
