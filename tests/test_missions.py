from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.missions import parse_mission_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_mission_document(game_install: GameInstall) -> None:
    document = parse_mission_document(
        _read_text(game_install.representative_files()["mission_sample"])
    )

    assert document.names() == ("generic_conquer_province",)

    definition = document.get_definition("generic_conquer_province")
    assert definition is not None
    assert definition.icon == "generic_conquer_province"
    assert definition.repeatable is True
    assert definition.player_playstyle == "military"
    assert definition.visible is not None
    assert definition.enabled is not None
    assert definition.on_start is not None
    assert definition.on_completion is not None
    assert len(definition.tasks) > 5

    war_chest = definition.get_task("mission_war_chest")
    assert war_chest is not None
    assert war_chest.icon == "court_accounting"
    assert war_chest.duration == 365
    assert war_chest.requires == ()
    assert war_chest.on_monthly is not None

    restore_province = definition.get_task("mission_restore_province")
    assert restore_province is not None
    assert restore_province.requires == ("mission_conquer_province", "mission_war_chest")


def test_parse_mission_document_with_pack_and_tasks() -> None:
    document = parse_mission_document(
        "sample_mission = {\n"
        "    header = sample_header\n"
        "    icon = sample_icon\n"
        "    repeatable = no\n"
        "    player_playstyle = diplomatic\n"
        "    chance = { base = 10 }\n"
        "    select_trigger = { looking_for_a = market }\n"
        "    on_start = { set_variable = foo }\n"
        "    first_task = {\n"
        "        icon = first_icon\n"
        "        requires = { }\n"
        "        final = no\n"
        "        duration = 30\n"
        "        enabled = { always = yes }\n"
        "    }\n"
        "    second_task = {\n"
        "        icon = second_icon\n"
        "        requires = { first_task }\n"
        "        final = yes\n"
        "        ai_will_do = { base = 5 }\n"
        "        on_completion = { add_stability = 1 }\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("sample_mission")
    assert definition is not None
    assert definition.header == "sample_header"
    assert definition.icon == "sample_icon"
    assert definition.repeatable is False
    assert definition.player_playstyle == "diplomatic"
    assert definition.chance is None
    assert definition.chance_object is not None
    assert definition.select_trigger is not None
    assert definition.on_start is not None
    assert definition.task_names() == ("first_task", "second_task")

    first_task = definition.get_task("first_task")
    assert first_task is not None
    assert first_task.final is False
    assert first_task.duration == 30
    assert first_task.requires == ()

    second_task = definition.get_task("second_task")
    assert second_task is not None
    assert second_task.final is True
    assert second_task.requires == ("first_task",)
    assert second_task.ai_will_do_object is not None
    assert second_task.on_completion is not None


def test_parse_mission_document_with_scalar_chance_and_ai_will_do() -> None:
    document = parse_mission_document(
        "another_mission = {\n"
        "    icon = another_icon\n"
        "    chance = 3600\n"
        "    ai_will_do = 10\n"
        "    task = {\n"
        "        icon = task_icon\n"
        "        ai_will_do = 5\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("another_mission")
    assert definition is not None
    assert definition.chance == "3600"
    assert definition.ai_will_do == "10"

    task = definition.get_task("task")
    assert task is not None
    assert task.ai_will_do == "5"
