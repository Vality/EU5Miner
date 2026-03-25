from __future__ import annotations

from eu5miner import (
    ContentPhase,
    GameInstall,
    ModUpdateAdvisory,
    ModUpdateWarning,
    VirtualFilesystem,
    apply_mod_update,
    format_mod_update_report,
    plan_mod_update,
)
from eu5miner.domains import (
    build_country_description_category_usage_document,
    build_linked_location_document,
    parse_country_description_category_document,
    parse_culture_document,
    parse_default_map_document,
    parse_event_document,
    parse_mod_metadata_document,
    parse_religion_document,
    parse_script_value_document,
    parse_scripted_list_document,
    parse_scripted_modifier_document,
    parse_scripted_relation_document,
    parse_scripted_trigger_document,
    parse_setup_country_document,
)
from eu5miner.formats.semantic import SemanticScalar


def test_root_package_exports_mod_workflow_surface() -> None:
    assert ContentPhase.IN_GAME.value == "in_game"
    assert GameInstall.__name__ == "GameInstall"
    assert VirtualFilesystem.__name__ == "VirtualFilesystem"
    assert callable(plan_mod_update)
    assert callable(apply_mod_update)
    assert callable(format_mod_update_report)
    assert ModUpdateAdvisory.__name__ == "ModUpdateAdvisory"
    assert ModUpdateWarning.__name__ == "ModUpdateWarning"


def test_domains_package_exports_curated_entrypoints() -> None:
    trigger_document = parse_scripted_trigger_document("test_trigger = { always = yes }\n")
    setup_document = parse_setup_country_document("FRA = { tier = kingdom }\n")
    event_document = parse_event_document("namespace = test\n\ntest.1 = { title = test }\n")
    metadata_document = parse_mod_metadata_document('{"name": "Test Mod"}')
    category_document = parse_country_description_category_document("military = {}\n")
    culture_document = parse_culture_document("example = { culture_groups = { alpha } }\n")
    religion_document = parse_religion_document("faith = { group = example tags = { tag } }\n")
    list_document = parse_scripted_list_document(
        "adult = { base = character conditions = { is_adult = yes } }\n"
    )
    modifier_document = parse_scripted_modifier_document(
        "my_modifier = { modifier = { add = 1 } }\n"
    )
    relation_document = parse_scripted_relation_document(
        "my_relation = { type = diplomacy relation_type = mutual }\n"
    )
    script_value_document = parse_script_value_document("my_value = { value = 5 }\n")
    default_map_document = parse_default_map_document("definitions = \"definitions.txt\"\n")

    assert trigger_document.names() == ("test_trigger",)
    assert setup_document.definitions[0].tag == "FRA"
    assert event_document.namespace == "test"
    assert metadata_document.name == "Test Mod"
    assert category_document.names() == ("military",)
    assert culture_document.names() == ("example",)
    assert religion_document.names() == ("faith",)
    assert list_document.names() == ("adult",)
    assert modifier_document.names() == ("my_modifier",)
    assert relation_document.names() == ("my_relation",)
    assert script_value_document.names() == ("my_value",)
    assert default_map_document.referenced_files.as_dict() == {
        "provinces": None,
        "rivers": None,
        "topology": None,
        "adjacencies": None,
        "setup": None,
        "ports": None,
        "location_templates": None,
    }
    definitions_entry = default_map_document.semantic_document.first_entry("definitions")
    assert definitions_entry is not None
    assert isinstance(definitions_entry.value, SemanticScalar)
    assert definitions_entry.value.text == '"definitions.txt"'
    assert callable(build_country_description_category_usage_document)
    assert callable(build_linked_location_document)
