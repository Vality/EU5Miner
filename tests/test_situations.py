from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.situations import parse_situation_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_situation_document(game_install: GameInstall) -> None:
    document = parse_situation_document(
        _read_text(game_install.representative_files()["situation_sample"])
    )

    assert document.names() == ("black_death",)

    definition = document.get_definition("black_death")
    assert definition is not None
    assert definition.monthly_spawn_chance == "monthly_spawn_chance_unique"
    assert definition.hint_tag == "hint_black_death"
    assert definition.can_start is not None
    assert definition.can_end is not None
    assert definition.visible is not None
    assert definition.on_start is not None
    assert definition.on_monthly is not None
    assert definition.tooltip is not None
    assert definition.on_ended is not None
    assert definition.is_data_map is True
    assert definition.map_color is not None


def test_parse_situation_document_with_end_trigger_and_secondary_color() -> None:
    document = parse_situation_document(
        "sample_situation = {\n"
        "    monthly_spawn_chance = 0\n"
        "    hint_tag = hint_sample\n"
        "    sample_situation_end_trigger = yes\n"
        "    can_start = { always = no }\n"
        "    can_end = { sample_situation_end_trigger = yes }\n"
        "    visible = { always = yes }\n"
        "    on_start = { set_variable = foo }\n"
        "    on_ending = { add_stability = -1 }\n"
        "    on_ended = { add_stability = 1 }\n"
        "    tooltip = { custom_tooltip = sample_tt }\n"
        "    map_color = { value = red }\n"
        "    secondary_map_color = { value = blue }\n"
        "    is_data_map = no\n"
        "}\n"
    )

    definition = document.get_definition("sample_situation")
    assert definition is not None
    assert definition.monthly_spawn_chance == "0"
    assert definition.hint_tag == "hint_sample"
    assert definition.end_trigger_flags == ("sample_situation_end_trigger",)
    assert definition.can_start is not None
    assert definition.can_end is not None
    assert definition.visible is not None
    assert definition.on_start is not None
    assert definition.on_ending is not None
    assert definition.on_ended is not None
    assert definition.tooltip is not None
    assert definition.map_color is not None
    assert definition.secondary_map_color is not None
    assert definition.is_data_map is False


def test_parse_situation_document_with_resolution_fields() -> None:
    document = parse_situation_document(
        "io_situation = {\n"
        "    monthly_spawn_chance = { base = 0.1 }\n"
        "    international_organization_type = io_type:council\n"
        "    resolution = resolution:sample_vote\n"
        "    voters = global_list:eligible_voters\n"
        "    visible = { always = yes }\n"
        "}\n"
    )

    definition = document.get_definition("io_situation")
    assert definition is not None
    assert definition.monthly_spawn_chance is None
    assert definition.monthly_spawn_chance_object is not None
    assert definition.international_organization_type == "io_type:council"
    assert definition.resolution == "resolution:sample_vote"
    assert definition.voters == "global_list:eligible_voters"
    assert definition.visible is not None
