from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.gui import parse_gui_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_gui_document_inline() -> None:
    document = parse_gui_document(
        "@scale = 42\n"
        "template sample_template {\n"
        "    text = \"HELLO\"\n"
        "}\n"
        "types SampleTypes {\n"
        "    type FancyWindow = window {\n"
        "        name = \"fancy_window\"\n"
        "    }\n"
        "}\n"
        "window = {\n"
        "    name = \"root_window\"\n"
        "    widgetid = \"root_widget\"\n"
        "}\n"
    )

    assert document.constant_names() == ("@scale",)
    assert document.get_constant("@scale") is not None
    assert document.get_constant("@scale").value_text == "42"
    assert document.template_names() == ("sample_template",)
    assert document.get_template("sample_template") is not None

    type_group = document.get_type_group("SampleTypes")
    assert type_group is not None
    assert type_group.definition_names() == ("FancyWindow",)

    type_definition = type_group.get_definition("FancyWindow")
    assert type_definition is not None
    assert type_definition.widget_kind == "window"
    assert type_definition.internal_name == '"fancy_window"'

    root_definition = document.get_root_definition("window")
    assert root_definition is not None
    assert root_definition.internal_name == '"root_window"'
    assert root_definition.widget_id == '"root_widget"'
    assert document.get_root_definition_by_name('"root_window"') is not None


@pytest.mark.timeout(5)
def test_parse_real_gui_templates_and_root_dialog(game_install: GameInstall) -> None:
    document = parse_gui_document(_read_text(game_install.representative_files()["gui_sample"]))

    assert document.get_template("agenda_scrollarea_setup") is not None
    assert document.get_template("advances_button_icon") is not None

    root_definition = document.get_root_definition("basic_priority_dialog")
    assert root_definition is not None
    assert root_definition.internal_name == '"agenda_view"'
    assert root_definition.widget_id == '"agenda_panel"'
    assert len(root_definition.body.find_entries("blockoverride")) >= 1


@pytest.mark.timeout(5)
def test_parse_real_gui_type_group(game_install: GameInstall) -> None:
    document = parse_gui_document(
        _read_text(game_install.representative_files()["gui_types_sample"])
    )

    assert document.get_constant("@illustration_wide") is not None
    assert document.get_constant("@banner_height") is not None

    type_group = document.get_type_group("EventWindows")
    assert type_group is not None

    age_event_window = type_group.get_definition("AgeEventWindow")
    assert age_event_window is not None
    assert age_event_window.widget_kind == "window"
    assert age_event_window.body.get_object("vbox") is not None

    root_window = document.get_root_definition("window")
    assert root_window is not None


@pytest.mark.timeout(5)
def test_parse_real_gui_window_by_internal_name(game_install: GameInstall) -> None:
    document = parse_gui_document(
        _read_text(game_install.representative_files()["gui_library_sample"])
    )

    root_definition = document.get_root_definition("window")
    assert root_definition is not None
    assert root_definition.internal_name == '"ui_library_window"'
    assert document.get_root_definition_by_name('"ui_library_window"') is not None
    assert document.get_type_group("UiLibrary") is not None
    assert document.get_template("text_section_description") is not None
