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
    build_linked_location_document,
    parse_default_map_document,
    parse_event_document,
    parse_mod_metadata_document,
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
    default_map_document = parse_default_map_document("definitions = \"definitions.txt\"\n")

    assert trigger_document.names() == ("test_trigger",)
    assert setup_document.definitions[0].tag == "FRA"
    assert event_document.namespace == "test"
    assert metadata_document.name == "Test Mod"
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
    assert callable(build_linked_location_document)
