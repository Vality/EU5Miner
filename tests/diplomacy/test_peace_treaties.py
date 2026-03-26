from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.diplomacy.peace_treaties import parse_peace_treaty_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_peace_treaty_document(game_install: GameInstall) -> None:
    document = parse_peace_treaty_document(
        _read_text(game_install.representative_files()["peace_treaty_sample"])
    )

    definition = document.get_definition("peace_humiliate")
    assert definition is not None
    assert definition.blocks_full_annexation is True
    assert definition.cost is not None
    assert definition.effect is not None
    assert definition.ai_desire is not None
    assert definition.select_triggers == ()


@pytest.mark.timeout(5)
def test_parse_real_variant_peace_treaty_documents(game_install: GameInstall) -> None:
    select_trigger_document = parse_peace_treaty_document(
        _read_text(game_install.representative_files()["peace_treaty_select_trigger_sample"])
    )
    treaty_document = parse_peace_treaty_document(
        _read_text(game_install.representative_files()["peace_treaty_secondary_sample"])
    )
    special_document = parse_peace_treaty_document(
        _read_text(game_install.representative_files()["peace_treaty_special_sample"])
    )
    exclusive_document = parse_peace_treaty_document(
        _read_text(game_install.representative_files()["peace_treaty_exclusive_sample"])
    )

    steal_maps = select_trigger_document.get_definition("steal_maps_treaty")
    assert steal_maps is not None
    assert steal_maps.collate_targets is True
    assert len(steal_maps.select_triggers) == 1
    assert steal_maps.select_triggers[0].looking_for_a == "area"
    assert steal_maps.select_triggers[0].columns[0].data == "name"
    assert steal_maps.select_triggers[0].none_available_msg_key == '"steal_maps_no_areas"'
    assert steal_maps.select_triggers[0].enabled is not None

    force_tributary = treaty_document.get_definition("force_tributary")
    assert force_tributary is not None
    assert force_tributary.base_antagonism == "20"
    assert force_tributary.antagonism_type == "antagonism_force_tributary"
    assert force_tributary.category == "country"

    religious_supremacy = special_document.get_definition("religious_supremacy")
    assert religious_supremacy is not None
    assert religious_supremacy.ai_force_add is True
    assert religious_supremacy.potential is not None
    assert religious_supremacy.effect is not None

    dismantle_fortifications = exclusive_document.get_definition("dismantle_fortifications")
    assert dismantle_fortifications is not None
    assert dismantle_fortifications.category == "dismantle_fort"
    assert dismantle_fortifications.are_targets_exclusive is True
    assert dismantle_fortifications.select_triggers[0].source == "recipient"


def test_peace_treaty_parses_inline_selection_fields() -> None:
    document = parse_peace_treaty_document(
        "sample_treaty = {\n"
        "    base_antagonism = { value = 5 }\n"
        "    show_tags_in_ui = yes\n"
        "    custom_tags = { maritime colonial }\n"
        "    select_trigger = {\n"
        "        looking_for_a = location\n"
        "        only_color_selectable = yes\n"
        "        visible = { always = yes }\n"
        "    }\n"
        "}\n"
    )

    definition = document.get_definition("sample_treaty")
    assert definition is not None
    assert isinstance(definition.base_antagonism, SemanticObject)
    assert definition.show_tags_in_ui is True
    assert definition.custom_tags == ("maritime", "colonial")
    assert definition.select_triggers[0].only_color_selectable is True
    assert definition.select_triggers[0].visible is not None
