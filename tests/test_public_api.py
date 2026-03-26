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
    DiplomacyGraphCatalog,
    DiplomacyGraphReport,
    GovernmentReformDefinition,
    GovernmentReformDocument,
    GovernmentTypeDefinition,
    GovernmentTypeDocument,
    LawDefinition,
    LawDocument,
    LawPolicyCatalog,
    LawPolicyDefinition,
    UnitAbilityDefinition,
    UnitAbilityDocument,
    UnitCategoryDefinition,
    UnitCategoryDocument,
    UnitModifierValue,
    UnitTypeDefinition,
    UnitTypeDocument,
    build_diplomacy_graph_catalog,
    build_diplomacy_graph_report,
    build_law_policy_catalog,
    build_war_flow_catalog,
    build_country_description_category_usage_document,
    build_linked_location_document,
    build_on_action_catalog_document,
    collect_casus_belli_references,
    collect_country_interaction_references,
    collect_subject_type_references,
    parse_attribute_column_document,
    parse_building_category_document,
    parse_building_type_document,
    parse_casus_belli_document,
    parse_character_interaction_document,
    parse_country_description_category_document,
    parse_country_interaction_document,
    parse_culture_document,
    parse_default_map_document,
    parse_employment_system_document,
    parse_event_document,
    parse_generic_action_document,
    parse_government_reform_document,
    parse_government_type_document,
    parse_goods_demand_category_document,
    parse_goods_demand_document,
    parse_goods_document,
    parse_law_document,
    parse_mod_metadata_document,
    parse_on_action_document,
    parse_on_action_documentation,
    parse_peace_treaty_document,
    parse_price_document,
    parse_production_method_document,
    parse_religion_document,
    parse_script_value_document,
    parse_scripted_list_document,
    parse_scripted_modifier_document,
    parse_scripted_relation_document,
    parse_scripted_trigger_document,
    parse_subject_military_stance_document,
    parse_subject_type_document,
    parse_setup_country_document,
    parse_unit_ability_document,
    parse_unit_category_document,
    parse_unit_type_document,
    parse_wargoal_document,
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
    casus_belli_document = parse_casus_belli_document(
        "sample_cb = { war_goal_type = superiority trade = yes }\n"
    )
    character_interaction_document = parse_character_interaction_document(
        "sample_character_interaction = { message = yes on_own_nation = yes }\n"
    )
    attribute_column_document = parse_attribute_column_document(
        "market = { name = { widget = default_text_column } }\n"
    )
    building_type_document = parse_building_type_document(
        "granary = { category = infrastructure_category pop_type = peasants }\n"
    )
    country_interaction_document = parse_country_interaction_document(
        "sample_country_interaction = { type = diplomacy category = CATEGORY_ACTIONS }\n"
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
    government_type_document = parse_government_type_document(
        "monarchy = { heir_selection = cognatic government_power = legitimacy }\n"
    )
    government_reform_document = parse_government_reform_document(
        "sample_reform = { government = monarchy years = 2 country_modifier = { add = 1 } }\n"
    )
    law_document = parse_law_document(
        "sample_law = {\n"
        "    law_category = administrative\n"
        "    policy_a = {\n"
        "        years = 2\n"
        "        country_modifier = { add = 1 }\n"
        "    }\n"
        "}\n"
    )
    peace_treaty_document = parse_peace_treaty_document(
        "peace_example = { potential = { scope:war = { casus_belli ?= casus_belli:sample_cb } } effect = { make_subject_of = { type = subject_type:sample_subject } } }\n"
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
    subject_type_document = parse_subject_type_document(
        "sample_subject = { level = 1 allow_subjects = no }\n"
    )
    subject_stance_document = parse_subject_military_stance_document(
        "sample_stance = { is_default = yes chase_navy_priority = 4 }\n"
    )
    unit_type_document = parse_unit_type_document(
        "sample_unit = { category = army_infantry buildable = yes }\n"
    )
    unit_ability_document = parse_unit_ability_document(
        "sample_ability = { toggle = yes army_only = yes }\n"
    )
    unit_category_document = parse_unit_category_document(
        "sample_category = { is_army = yes startup_amount = 1 }\n"
    )
    wargoal_document = parse_wargoal_document(
        "sample_goal = { type = superiority attacker = { conquer_cost = 1 } }\n"
    )
    diplomacy_catalog = build_diplomacy_graph_catalog(
        casus_belli_documents=(casus_belli_document,),
        wargoal_documents=(wargoal_document,),
        peace_treaty_documents=(peace_treaty_document,),
        subject_type_documents=(subject_type_document,),
        country_interaction_documents=(country_interaction_document,),
        character_interaction_documents=(character_interaction_document,),
    )
    diplomacy_report = build_diplomacy_graph_report(diplomacy_catalog)
    law_catalog = build_law_policy_catalog((law_document,))
    war_catalog = build_war_flow_catalog(
        casus_belli_documents=(casus_belli_document,),
        wargoal_documents=(wargoal_document,),
        peace_treaty_documents=(peace_treaty_document,),
        subject_type_documents=(subject_type_document,),
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
    assert casus_belli_document.names() == ("sample_cb",)
    assert character_interaction_document.names() == ("sample_character_interaction",)
    assert attribute_column_document.names() == ("market",)
    assert building_type_document.names() == ("granary",)
    assert country_interaction_document.names() == ("sample_country_interaction",)
    assert goods_document.names() == ("iron",)
    assert goods_demand_category_document.names() == ("building_construction",)
    assert goods_demand_document.names() == ("sample_demand",)
    assert production_method_document.names() == ("maintenance",)
    assert category_document.names() == ("military",)
    assert culture_document.names() == ("example",)
    assert employment_system_document.names() == ("equality",)
    assert generic_action_document.names() == ("create_market",)
    assert government_type_document.names() == ("monarchy",)
    assert government_reform_document.names() == ("sample_reform",)
    assert law_document.names() == ("sample_law",)
    assert peace_treaty_document.names() == ("peace_example",)
    assert price_document.names() == ("build_road",)
    assert religion_document.names() == ("faith",)
    assert list_document.names() == ("adult",)
    assert modifier_document.names() == ("my_modifier",)
    assert relation_document.names() == ("my_relation",)
    assert subject_type_document.names() == ("sample_subject",)
    assert subject_stance_document.names() == ("sample_stance",)
    assert unit_type_document.names() == ("sample_unit",)
    assert unit_ability_document.names() == ("sample_ability",)
    assert unit_category_document.names() == ("sample_category",)
    assert wargoal_document.names() == ("sample_goal",)
    assert script_value_document.names() == ("my_value",)
    assert collect_casus_belli_references(peace_treaty_document.definitions[0].body) == (
        "sample_cb",
    )
    assert collect_subject_type_references(peace_treaty_document.definitions[0].body) == (
        "sample_subject",
    )
    assert collect_country_interaction_references(country_interaction_document.definitions[0].body) == ()
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
    assert callable(build_war_flow_catalog)
    assert callable(build_diplomacy_graph_catalog)
    assert callable(build_diplomacy_graph_report)
    assert callable(build_law_policy_catalog)
    assert callable(build_country_description_category_usage_document)
    assert callable(build_linked_location_document)
    assert war_catalog.get_peace_treaty("peace_example") is not None
    assert war_catalog.get_subject_type("sample_subject") is not None
    assert diplomacy_catalog.get_subject_type("sample_subject") is not None
    assert law_catalog.get_policy("policy_a") is not None
    assert isinstance(diplomacy_catalog, DiplomacyGraphCatalog)
    assert isinstance(diplomacy_report, DiplomacyGraphReport)
    assert isinstance(law_catalog, LawPolicyCatalog)
    assert UnitModifierValue.__name__ == "UnitModifierValue"
    assert UnitTypeDefinition.__name__ == "UnitTypeDefinition"
    assert UnitTypeDocument.__name__ == "UnitTypeDocument"
    assert UnitAbilityDefinition.__name__ == "UnitAbilityDefinition"
    assert UnitAbilityDocument.__name__ == "UnitAbilityDocument"
    assert UnitCategoryDefinition.__name__ == "UnitCategoryDefinition"
    assert UnitCategoryDocument.__name__ == "UnitCategoryDocument"
    assert GovernmentTypeDefinition.__name__ == "GovernmentTypeDefinition"
    assert GovernmentTypeDocument.__name__ == "GovernmentTypeDocument"
    assert GovernmentReformDefinition.__name__ == "GovernmentReformDefinition"
    assert GovernmentReformDocument.__name__ == "GovernmentReformDocument"
    assert LawDefinition.__name__ == "LawDefinition"
    assert LawDocument.__name__ == "LawDocument"
    assert LawPolicyDefinition.__name__ == "LawPolicyDefinition"
