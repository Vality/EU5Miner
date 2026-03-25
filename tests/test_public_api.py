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
    build_on_action_catalog_document,
    parse_attribute_column_document,
    parse_building_category_document,
    parse_building_type_document,
    parse_country_description_category_document,
    parse_culture_document,
    parse_default_map_document,
    parse_employment_system_document,
    parse_event_document,
    parse_generic_action_document,
    parse_goods_demand_category_document,
    parse_goods_demand_document,
    parse_goods_document,
    parse_mod_metadata_document,
    parse_on_action_document,
    parse_on_action_documentation,
    parse_price_document,
    parse_production_method_document,
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
    on_action_document = parse_on_action_document("on_example = { events = { test.1 } }\n")
    on_action_documentation = parse_on_action_documentation(
        "On Action Documentation:\n\n"
        "--------------------\n\n"
        "on_example:\n"
        "From Code: Yes\n"
        "Expected Scope: country\n"
    )
    building_category_document = parse_building_category_document(
        "trade_category = {}\n"
    )
    attribute_column_document = parse_attribute_column_document(
        "market = { name = { widget = default_text_column } }\n"
    )
    building_type_document = parse_building_type_document(
        "granary = { category = infrastructure_category pop_type = peasants }\n"
    )
    goods_document = parse_goods_document(
        "iron = { method = mining category = raw_material }\n"
    )
    goods_demand_category_document = parse_goods_demand_category_document(
        "building_construction = { display = integer }\n"
    )
    goods_demand_document = parse_goods_demand_document(
        "sample_demand = { iron = 0.5 category = special_demands }\n"
    )
    production_method_document = parse_production_method_document(
        "maintenance = { tools = 0.1 category = building_maintenance }\n"
    )
    category_document = parse_country_description_category_document("military = {}\n")
    culture_document = parse_culture_document("example = { culture_groups = { alpha } }\n")
    employment_system_document = parse_employment_system_document(
        "equality = { priority = { value = 1 } }\n"
    )
    generic_action_document = parse_generic_action_document(
        "create_market = { type = owncountry select_trigger = { looking_for_a = market } }\n"
    )
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
    price_document = parse_price_document("build_road = { gold = 10 }\n")
    script_value_document = parse_script_value_document("my_value = { value = 5 }\n")
    default_map_document = parse_default_map_document("definitions = \"definitions.txt\"\n")

    assert trigger_document.names() == ("test_trigger",)
    assert setup_document.definitions[0].tag == "FRA"
    assert event_document.namespace == "test"
    assert metadata_document.name == "Test Mod"
    assert on_action_document.names() == ("on_example",)
    assert on_action_documentation.names() == ("on_example",)
    assert building_category_document.names() == ("trade_category",)
    assert attribute_column_document.names() == ("market",)
    assert building_type_document.names() == ("granary",)
    assert goods_document.names() == ("iron",)
    assert goods_demand_category_document.names() == ("building_construction",)
    assert goods_demand_document.names() == ("sample_demand",)
    assert production_method_document.names() == ("maintenance",)
    assert category_document.names() == ("military",)
    assert culture_document.names() == ("example",)
    assert employment_system_document.names() == ("equality",)
    assert generic_action_document.names() == ("create_market",)
    assert price_document.names() == ("build_road",)
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
    assert callable(build_on_action_catalog_document)
    assert callable(build_country_description_category_usage_document)
    assert callable(build_linked_location_document)
