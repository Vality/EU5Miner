from __future__ import annotations

import eu5miner.domains.diplomacy as diplomacy_api
import eu5miner.domains.economy as economy_api
import eu5miner.domains.government as government_api
import eu5miner.domains.localization as localization_api
import eu5miner.domains.map as map_api
import eu5miner.domains.religion as religion_api
import eu5miner.domains.units as units_api
from eu5miner.domains.attribute_columns import parse_attribute_column_document
from eu5miner.domains.diplomacy import (
    DiplomacyGraphCatalog,
    WarFlowCatalog,
    build_diplomacy_graph_catalog,
    build_war_flow_catalog,
    parse_casus_belli_document,
    parse_character_interaction_document,
    parse_country_interaction_document,
    parse_generic_action_document,
    parse_peace_treaty_document,
    parse_subject_type_document,
    parse_wargoal_document,
)
from eu5miner.domains.economy import (
    MarketCatalog,
    build_market_catalog,
    parse_goods_document,
    parse_price_document,
)
from eu5miner.domains.government import (
    GovernmentCatalog,
    build_government_catalog,
    parse_estate_document,
    parse_estate_privilege_document,
    parse_government_reform_document,
    parse_government_type_document,
    parse_law_document,
)
from eu5miner.domains.localization import (
    LocalizationBundle,
    build_localization_bundle,
    parse_effect_localization_document,
)
from eu5miner.domains.map import (
    DefaultMapDocument,
    build_linked_location_document,
    parse_country_location_document,
    parse_default_map_document,
    parse_location_hierarchy_document,
    parse_location_setup_document,
)
from eu5miner.domains.religion import (
    HolySiteCatalog,
    ReligionCatalog,
    build_holy_site_catalog,
    build_religion_catalog,
    parse_holy_site_document,
    parse_holy_site_type_document,
    parse_religion_document,
    parse_religious_aspect_document,
)
from eu5miner.domains.units import UnitCategoryDocument, parse_unit_category_document

EXPECTED_DIPLOMACY_EXPORTS = {
    "CasusBelliDefinition",
    "CasusBelliDocument",
    "CharacterInteractionColumn",
    "CharacterInteractionDefinition",
    "CharacterInteractionDocument",
    "CharacterInteractionSelectTrigger",
    "CountryInteractionColumn",
    "CountryInteractionDefinition",
    "CountryInteractionDocument",
    "CountryInteractionSelectTrigger",
    "DiplomacyGraphCatalog",
    "DiplomacyGraphReport",
    "DiplomacyReferenceEdge",
    "GenericActionColumn",
    "GenericActionDefinition",
    "GenericActionDocument",
    "GenericActionSelectTrigger",
    "PeaceTreatyColumn",
    "PeaceTreatyDefinition",
    "PeaceTreatyDocument",
    "PeaceTreatySelectTrigger",
    "SubjectTypeDefinition",
    "SubjectTypeDocument",
    "WarFlowCatalog",
    "WarFlowReport",
    "WarReferenceEdge",
    "WargoalDefinition",
    "WargoalDocument",
    "WargoalParticipantDefinition",
    "build_diplomacy_graph_catalog",
    "build_diplomacy_graph_report",
    "build_war_flow_catalog",
    "build_war_flow_report",
    "collect_casus_belli_references",
    "collect_country_interaction_references",
    "collect_subject_type_references",
    "parse_casus_belli_document",
    "parse_character_interaction_document",
    "parse_country_interaction_document",
    "parse_generic_action_document",
    "parse_peace_treaty_document",
    "parse_subject_type_document",
    "parse_wargoal_document",
}

EXPECTED_ECONOMY_EXPORTS = {
    "EmploymentSystemDefinition",
    "EmploymentSystemDocument",
    "GoodsAmount",
    "GoodsDefinition",
    "GoodsDemandAmount",
    "GoodsDemandCategoryDefinition",
    "GoodsDemandCategoryDocument",
    "GoodsDemandDefinition",
    "GoodsDemandDocument",
    "GoodsDocument",
    "MarketCatalog",
    "MarketReferenceEdge",
    "MarketReport",
    "PriceDefinition",
    "PriceDocument",
    "ProductionMethodDefinition",
    "ProductionMethodDocument",
    "ProductionMethodInput",
    "ScriptedGoodsDemand",
    "build_market_catalog",
    "build_market_report",
    "parse_employment_system_document",
    "parse_goods_demand_category_document",
    "parse_goods_demand_document",
    "parse_goods_document",
    "parse_price_document",
    "parse_production_method_document",
}

EXPECTED_GOVERNMENT_EXPORTS = {
    "EstateDefinition",
    "EstateDocument",
    "EstatePrivilegeDefinition",
    "EstatePrivilegeDocument",
    "GovernmentCatalog",
    "GovernmentReferenceEdge",
    "GovernmentReformDefinition",
    "GovernmentReformDocument",
    "GovernmentReport",
    "GovernmentTypeDefinition",
    "GovernmentTypeDocument",
    "LawDefinition",
    "LawDocument",
    "LawPolicyCatalog",
    "LawPolicyDefinition",
    "ParliamentAgendaDefinition",
    "ParliamentAgendaDocument",
    "ParliamentIssueDefinition",
    "ParliamentIssueDocument",
    "ParliamentTypeDefinition",
    "ParliamentTypeDocument",
    "build_government_catalog",
    "build_government_report",
    "build_law_policy_catalog",
    "parse_estate_document",
    "parse_estate_privilege_document",
    "parse_government_reform_document",
    "parse_government_type_document",
    "parse_law_document",
    "parse_parliament_agenda_document",
    "parse_parliament_issue_document",
    "parse_parliament_type_document",
}

EXPECTED_LOCALIZATION_EXPORTS = {
    "CustomizableLocalizationDefinition",
    "CustomizableLocalizationDocument",
    "CustomizableLocalizationText",
    "EffectLocalizationDefinition",
    "EffectLocalizationDocument",
    "LocalizationBundle",
    "LocalizationBundleEntry",
    "LocalizationReference",
    "LocalizationVariant",
    "TriggerLocalizationDefinition",
    "TriggerLocalizationDocument",
    "build_localization_bundle",
    "collect_customizable_localization_references",
    "collect_effect_localization_references",
    "collect_trigger_localization_references",
    "find_missing_localization_references",
    "parse_customizable_localization_document",
    "parse_effect_localization_document",
    "parse_trigger_localization_document",
}

EXPECTED_MAP_EXPORTS = {
    "CountryLocationDefinition",
    "CountryLocationDocument",
    "CountryLocationGroup",
    "DefaultMapDocument",
    "DefaultMapReferencedFiles",
    "LinkedLocationDefinition",
    "LinkedLocationDocument",
    "LocationCountryReference",
    "LocationHierarchyDefinition",
    "LocationHierarchyDocument",
    "LocationSetupDefinition",
    "LocationSetupDocument",
    "MapAdjacencyDefinition",
    "MapAdjacencyDocument",
    "MapPortDefinition",
    "MapPortDocument",
    "SetupCountryDefinition",
    "SetupCountryDocument",
    "SoundTollDefinition",
    "build_linked_location_document",
    "parse_country_location_document",
    "parse_default_map_document",
    "parse_location_hierarchy_document",
    "parse_location_setup_document",
    "parse_map_adjacencies_document",
    "parse_map_ports_document",
    "parse_setup_country_document",
}

EXPECTED_RELIGION_EXPORTS = {
    "HolySiteCatalog",
    "HolySiteDefinition",
    "HolySiteDocument",
    "HolySiteReferenceEdge",
    "HolySiteReport",
    "HolySiteTypeDefinition",
    "HolySiteTypeDocument",
    "ReligionCatalog",
    "ReligionDefinition",
    "ReligionDocument",
    "ReligionOpinion",
    "ReligionReferenceEdge",
    "ReligionReport",
    "ReligiousAspectDefinition",
    "ReligiousAspectDocument",
    "ReligiousAspectOpinion",
    "ReligiousFactionDefinition",
    "ReligiousFactionDocument",
    "ReligiousFigureDefinition",
    "ReligiousFigureDocument",
    "ReligiousFocusDefinition",
    "ReligiousFocusDocument",
    "ReligiousSchoolDefinition",
    "ReligiousSchoolDocument",
    "build_holy_site_catalog",
    "build_holy_site_report",
    "build_religion_catalog",
    "build_religion_report",
    "parse_holy_site_document",
    "parse_holy_site_type_document",
    "parse_religion_document",
    "parse_religious_aspect_document",
    "parse_religious_faction_document",
    "parse_religious_figure_document",
    "parse_religious_focus_document",
    "parse_religious_school_document",
}

EXPECTED_UNITS_EXPORTS = {
    "UnitAbilityDefinition",
    "UnitAbilityDocument",
    "UnitCategoryDefinition",
    "UnitCategoryDocument",
    "UnitMercenariesPerLocation",
    "UnitModifierBearingLike",
    "UnitModifierValue",
    "UnitTypeDefinition",
    "UnitTypeDocument",
    "get_unit_modifier",
    "parse_unit_ability_document",
    "parse_unit_category_document",
    "parse_unit_type_document",
}


def test_grouped_packages_publish_package_level_entrypoints() -> None:
    assert set(diplomacy_api.__all__) == EXPECTED_DIPLOMACY_EXPORTS
    assert set(economy_api.__all__) == EXPECTED_ECONOMY_EXPORTS
    assert set(government_api.__all__) == EXPECTED_GOVERNMENT_EXPORTS
    assert set(localization_api.__all__) == EXPECTED_LOCALIZATION_EXPORTS
    assert set(map_api.__all__) == EXPECTED_MAP_EXPORTS
    assert set(religion_api.__all__) == EXPECTED_RELIGION_EXPORTS
    assert set(units_api.__all__) == EXPECTED_UNITS_EXPORTS


def test_grouped_diplomacy_package_exports_both_helper_layers() -> None:
    casus_belli_document = parse_casus_belli_document(
        "sample_cb = { war_goal_type = superiority }\n"
    )
    wargoal_document = parse_wargoal_document(
        "superiority = { type = superiority attacker = { conquer_cost = 1 } }\n"
    )
    peace_treaty_document = parse_peace_treaty_document(
        "peace_example = { effect = { make_subject_of = { type = "
        "subject_type:sample_subject } } }\n"
    )
    subject_type_document = parse_subject_type_document(
        "sample_subject = { level = 1 allow_subjects = no }\n"
    )
    country_interaction_document = parse_country_interaction_document(
        "sample_country_interaction = { type = diplomacy }\n"
    )
    character_interaction_document = parse_character_interaction_document(
        "sample_character_interaction = { message = yes }\n"
    )

    war_catalog = build_war_flow_catalog(
        casus_belli_documents=(casus_belli_document,),
        wargoal_documents=(wargoal_document,),
        peace_treaty_documents=(peace_treaty_document,),
        subject_type_documents=(subject_type_document,),
    )
    diplomacy_catalog = build_diplomacy_graph_catalog(
        casus_belli_documents=(casus_belli_document,),
        wargoal_documents=(wargoal_document,),
        peace_treaty_documents=(peace_treaty_document,),
        subject_type_documents=(subject_type_document,),
        country_interaction_documents=(country_interaction_document,),
        character_interaction_documents=(character_interaction_document,),
    )

    assert isinstance(war_catalog, WarFlowCatalog)
    assert isinstance(diplomacy_catalog, DiplomacyGraphCatalog)


def test_grouped_map_and_localization_packages_support_inline_usage() -> None:
    default_map_document = parse_default_map_document('definitions = "definitions.txt"\n')
    hierarchy_document = parse_location_hierarchy_document(
        "world = { region = { area = { province = { stockholm } } } }\n"
    )
    country_document = parse_country_location_document(
        "countries = { countries = { SWE = { own_control_core = { stockholm } "
        "capital = stockholm } } }\n"
    )
    setup_document = parse_location_setup_document(
        "locations = { stockholm = { timed_modifiers = { } } }\n"
    )
    linked_document = build_linked_location_document(
        hierarchy_document,
        country_document,
        setup_document,
    )
    effect_document = parse_effect_localization_document(
        "sample_effect = { global = SAMPLE_EFFECT }\n"
    )
    bundle = build_localization_bundle((("sample.yml", 'l_english:\nSAMPLE_EFFECT: "Effect"\n'),))

    assert isinstance(default_map_document, DefaultMapDocument)
    assert linked_document.get_location("stockholm") is not None
    assert len(effect_document.definitions) == 1
    assert isinstance(bundle, LocalizationBundle)


def test_grouped_economy_and_units_packages_support_inline_usage() -> None:
    goods_document = parse_goods_document(
        "iron = {\n"
        "    method = mining\n"
        "    category = raw_material\n"
        "    default_market_price = 3\n"
        "}\n"
    )
    price_document = parse_price_document("build_road = { gold = 10 }\n")
    generic_action_document = parse_generic_action_document(
        "create_market = {\n"
        "    type = owncountry\n"
        "    select_trigger = {\n"
        "        looking_for_a = market\n"
        "    }\n"
        "}\n"
    )
    attribute_column_document = parse_attribute_column_document(
        "market = { name = { widget = default_text_column } }\n"
    )
    market_catalog = build_market_catalog(
        goods_documents=(goods_document,),
        price_documents=(price_document,),
        generic_action_documents=(generic_action_document,),
        attribute_column_documents=(attribute_column_document,),
    )
    unit_category_document = parse_unit_category_document(
        "sample_category = { is_army = yes startup_amount = 1 }\n"
    )

    assert isinstance(market_catalog, MarketCatalog)
    assert market_catalog.get_market_actions()[0].name == "create_market"
    assert isinstance(unit_category_document, UnitCategoryDocument)


def test_grouped_government_and_religion_packages_support_inline_usage() -> None:
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
    estate_document = parse_estate_document(
        "sample_estate = { color = pop_nobles power_per_pop = 25 tax_per_pop = 100 ruler = yes }\n"
    )
    estate_privilege_document = parse_estate_privilege_document(
        "sample_privilege = { estate = sample_estate country_modifier = { add = 1 } }\n"
    )
    government_catalog = build_government_catalog(
        government_type_documents=(government_type_document,),
        government_reform_documents=(government_reform_document,),
        law_documents=(law_document,),
        estate_documents=(estate_document,),
        estate_privilege_documents=(estate_privilege_document,),
    )

    holy_site_type_document = parse_holy_site_type_document(
        "temple = { location_modifier = { add = 1 } }\n"
    )
    holy_site_document = parse_holy_site_document(
        "sample_site = { location = rome type = temple importance = 4 religions = { faith } }\n"
    )
    religion_document = parse_religion_document(
        "faith = { group = example religious_aspects = { sample_aspect } }\n"
    )
    religious_aspect_document = parse_religious_aspect_document(
        "sample_aspect = { religion = faith enabled = { always = yes } modifier = { add = 1 } }\n"
    )
    holy_site_catalog = build_holy_site_catalog((holy_site_type_document,), (holy_site_document,))
    religion_catalog = build_religion_catalog(
        religion_documents=(religion_document,),
        religious_aspect_documents=(religious_aspect_document,),
        holy_site_documents=(holy_site_document,),
    )

    assert isinstance(government_catalog, GovernmentCatalog)
    assert isinstance(holy_site_catalog, HolySiteCatalog)
    assert isinstance(religion_catalog, ReligionCatalog)
