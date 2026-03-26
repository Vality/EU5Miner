from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.units.unit_abilities import parse_unit_ability_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_unit_ability_document(game_install: GameInstall) -> None:
    document = parse_unit_ability_document(
        _read_text(game_install.representative_files()["unit_ability_sample"])
    )

    definition = document.get_definition("drill_army")
    assert definition is not None
    assert definition.duration == "-1"
    assert definition.toggle is True
    assert definition.army_only is True
    assert definition.cancel_on_combat_end is True
    assert definition.cancel_on_move is True
    assert definition.map is True
    assert definition.allow is not None
    assert definition.modifier is not None
    assert definition.start_effect is not None
    assert definition.finished_when is not None
    assert definition.ai_will_do is not None
    assert definition.ai_will_revoke is not None


@pytest.mark.timeout(5)
def test_parse_real_variant_unit_ability_document(game_install: GameInstall) -> None:
    document = parse_unit_ability_document(
        _read_text(game_install.representative_files()["unit_ability_secondary_sample"])
    )

    definition = document.get_definition("scorch_earth")
    assert definition is not None
    assert definition.toggle is False
    assert definition.army_only is True
    assert definition.map is True
    assert definition.allow is not None
    assert definition.start_effect is not None
    assert definition.ai_will_do is not None


def test_unit_ability_parses_inline_variant_fields() -> None:
    document = parse_unit_ability_document(
        "sample_ability = {\n"
        "    hidden = { always = no }\n"
        "    allow = { always = yes }\n"
        "    ai_allow_plan_slowdown = yes\n"
        "    soundeffect = unit_sound\n"
        "    navy_only = yes\n"
        "    cancel_on_combat = yes\n"
        "    confirm = no\n"
        "    finish_effect = { add = 1 }\n"
        "    on_entering_location = { add = 2 }\n"
        "    idle_entity_state = idle\n"
        "    move_entity_state = move\n"
        "    available_states = { idle move }\n"
        "    block_reorg = yes\n"
        "}\n"
    )

    definition = document.get_definition("sample_ability")
    assert definition is not None
    assert definition.hidden is not None
    assert definition.allow is not None
    assert definition.ai_allow_plan_slowdown is True
    assert definition.soundeffect == "unit_sound"
    assert definition.navy_only is True
    assert definition.cancel_on_combat is True
    assert definition.confirm is False
    assert definition.finish_effect is not None
    assert definition.on_entering_location is not None
    assert definition.idle_entity_state == "idle"
    assert definition.move_entity_state == "move"
    assert definition.available_states is not None
    assert definition.block_reorg is True

