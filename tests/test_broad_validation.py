from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from eu5miner import ContentPhase
from eu5miner.domains.attribute_columns import parse_attribute_column_document
from eu5miner.domains.building_categories import parse_building_category_document
from eu5miner.domains.building_types import parse_building_type_document
from eu5miner.domains.country_description_categories import (
    build_country_description_category_usage_document,
    parse_country_description_category_document,
)
from eu5miner.domains.cultures import parse_culture_document
from eu5miner.domains.diplomacy import build_war_flow_catalog, build_war_flow_report
from eu5miner.domains.diplomacy.casus_belli import parse_casus_belli_document
from eu5miner.domains.diplomacy.character_interactions import parse_character_interaction_document
from eu5miner.domains.diplomacy.country_interactions import parse_country_interaction_document
from eu5miner.domains.diplomacy.diplomacy import (
    build_diplomacy_graph_catalog,
    build_diplomacy_graph_report,
)
from eu5miner.domains.diplomacy.generic_actions import parse_generic_action_document
from eu5miner.domains.diplomacy.peace_treaties import parse_peace_treaty_document
from eu5miner.domains.diplomacy.subject_types import parse_subject_type_document
from eu5miner.domains.diplomacy.wargoals import parse_wargoal_document
from eu5miner.domains.disasters import parse_disaster_document
from eu5miner.domains.economy.employment_systems import parse_employment_system_document
from eu5miner.domains.economy.goods import parse_goods_document
from eu5miner.domains.economy.goods_demand_categories import parse_goods_demand_category_document
from eu5miner.domains.economy.goods_demands import parse_goods_demand_document
from eu5miner.domains.economy.prices import parse_price_document
from eu5miner.domains.economy.production_methods import parse_production_method_document
from eu5miner.domains.events import parse_event_document
from eu5miner.domains.frontend_content import (
    build_phase_localization_bundle,
    parse_main_menu_scenarios_document,
)
from eu5miner.domains.government import (
    build_government_catalog,
    build_government_report,
)
from eu5miner.domains.government.estate_privileges import parse_estate_privilege_document
from eu5miner.domains.government.estates import parse_estate_document
from eu5miner.domains.government.government_reforms import parse_government_reform_document
from eu5miner.domains.government.government_types import parse_government_type_document
from eu5miner.domains.government.laws import build_law_policy_catalog, parse_law_document
from eu5miner.domains.government.parliament_agendas import parse_parliament_agenda_document
from eu5miner.domains.government.parliament_issues import parse_parliament_issue_document
from eu5miner.domains.government.parliament_types import parse_parliament_type_document
from eu5miner.domains.institutions import parse_institution_document
from eu5miner.domains.localization.localization_bundles import (
    build_localization_bundle,
    collect_customizable_localization_references,
    find_missing_localization_references,
)
from eu5miner.domains.localization.localization_helpers import (
    parse_customizable_localization_document,
    parse_effect_localization_document,
    parse_trigger_localization_document,
)
from eu5miner.domains.map.location_setup_links import (
    build_linked_location_document,
    parse_country_location_document,
    parse_location_hierarchy_document,
    parse_location_setup_document,
)
from eu5miner.domains.map.map_csv_helpers import (
    parse_map_adjacencies_document,
    parse_map_ports_document,
)
from eu5miner.domains.map.map_text import parse_default_map_document
from eu5miner.domains.map.setup_countries import parse_setup_country_document
from eu5miner.domains.missions import parse_mission_document
from eu5miner.domains.mod_metadata import parse_mod_metadata_document
from eu5miner.domains.on_actions import (
    build_on_action_catalog_document,
    parse_on_action_document,
)
from eu5miner.domains.religion import build_religion_catalog, build_religion_report
from eu5miner.domains.religion.holy_site_types import parse_holy_site_type_document
from eu5miner.domains.religion.holy_sites import (
    build_holy_site_catalog,
    build_holy_site_report,
    parse_holy_site_document,
)
from eu5miner.domains.religion.religions import parse_religion_document
from eu5miner.domains.religion.religious_aspects import parse_religious_aspect_document
from eu5miner.domains.religion.religious_factions import parse_religious_faction_document
from eu5miner.domains.religion.religious_figures import parse_religious_figure_document
from eu5miner.domains.religion.religious_focuses import parse_religious_focus_document
from eu5miner.domains.religion.religious_schools import parse_religious_school_document
from eu5miner.domains.script_values import parse_script_value_document
from eu5miner.domains.scripted_effects import parse_scripted_effect_document
from eu5miner.domains.scripted_lists import parse_scripted_list_document
from eu5miner.domains.scripted_relations import parse_scripted_relation_document
from eu5miner.domains.scripted_triggers import parse_scripted_trigger_document
from eu5miner.domains.situations import parse_situation_document
from eu5miner.domains.societal_values import parse_societal_value_document
from eu5miner.domains.subject_military_stances import parse_subject_military_stance_document
from eu5miner.domains.units.unit_abilities import parse_unit_ability_document
from eu5miner.domains.units.unit_categories import parse_unit_category_document
from eu5miner.domains.units.unit_types import parse_unit_type_document
from eu5miner.formats.localization import parse_localization
from eu5miner.formats.map_csv import parse_semicolon_csv
from eu5miner.formats.metadata import parse_metadata_json
from eu5miner.source import GameInstall

pytestmark = pytest.mark.broad

_UNHANDLED = object()

_TEXT_ONLY_KEYS = {"policy_info"}

_LOCALIZATION_KEYS = {
    "english_effects_localization",
    "english_laws_localization",
    "english_triggers_localization",
    "loading_screen_localization_sample",
    "localization_sample",
}

_RELATION_KEYS = {
    "scripted_relation_sample",
    "scripted_relation_secondary_sample",
}

_CASUS_BELLI_KEYS = {
    "casus_belli_sample",
    "casus_belli_secondary_sample",
    "casus_belli_dense_sample",
    "casus_belli_subject_sample",
    "casus_belli_religious_sample",
    "casus_belli_trade_sample",
}

_PEACE_TREATY_KEYS = {
    "peace_treaty_sample",
    "peace_treaty_select_trigger_sample",
    "peace_treaty_secondary_sample",
    "peace_treaty_special_sample",
    "peace_treaty_exclusive_sample",
}

_SUBJECT_TYPE_KEYS = {
    "subject_type_sample",
    "subject_type_secondary_sample",
    "subject_type_colonial_sample",
    "subject_type_hre_sample",
    "subject_type_special_sample",
}

_CHARACTER_INTERACTION_KEYS = {
    "character_interaction_sample",
    "character_interaction_secondary_sample",
    "character_interaction_ui_sample",
}

_UNIT_TYPE_KEYS = {"unit_type_sample", "unit_type_secondary_sample"}
_UNIT_ABILITY_KEYS = {"unit_ability_sample", "unit_ability_secondary_sample"}
_UNIT_CATEGORY_KEYS = {"unit_category_sample", "unit_category_secondary_sample"}

_GOVERNMENT_REFORM_KEYS = {
    "government_reform_sample",
    "government_reform_secondary_sample",
    "government_reform_special_sample",
}

_LAW_KEYS = {
    "law_sample",
    "law_secondary_sample",
    "law_country_specific_sample",
    "law_io_sample",
    "law_io_secondary_sample",
}

_ESTATE_PRIVILEGE_KEYS = {
    "estate_privilege_sample",
    "estate_privilege_secondary_sample",
    "estate_privilege_special_sample",
}

_PARLIAMENT_TYPE_KEYS = {
    "parliament_type_sample",
    "parliament_type_secondary_sample",
}

_PARLIAMENT_AGENDA_KEYS = {
    "parliament_agenda_sample",
    "parliament_agenda_secondary_sample",
    "parliament_agenda_special_sample",
}

_PARLIAMENT_ISSUE_KEYS = {
    "parliament_issue_sample",
    "parliament_issue_secondary_sample",
    "parliament_issue_special_sample",
}

_INSTITUTION_KEYS = {"institution_sample", "institution_secondary_sample"}
_HOLY_SITE_KEYS = {"holy_site_sample", "holy_site_secondary_sample"}
_RELIGIOUS_ASPECT_KEYS = {"religious_aspect_sample", "religious_aspect_secondary_sample"}
_RELIGION_KEYS = {
    "religion_sample",
    "religion_secondary_sample",
    "religion_muslim_sample",
    "religion_tonal_sample",
    "religion_dharmic_sample",
}

_GOODS_KEYS = {"goods_sample", "goods_secondary_sample"}
_PRICE_KEYS = {"price_sample", "price_secondary_sample"}
_GOODS_DEMAND_KEYS = {
    "goods_demand_sample",
    "goods_demand_secondary_sample",
    "goods_demand_tertiary_sample",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def _is_text_only_key(key: str) -> bool:
    return key in _TEXT_ONLY_KEYS or key.endswith("_readme") or key.endswith("_info")


def _parse_representative_sample(key: str, text: str) -> Any:
    if key == "event_sample":
        return parse_event_document(text)
    if key == "mission_sample":
        return parse_mission_document(text)
    if key == "situation_sample":
        return parse_situation_document(text)
    if key == "disaster_sample":
        return parse_disaster_document(text)
    if key == "customizable_localization_sample":
        return parse_customizable_localization_document(text)
    if key == "effect_localization_sample":
        return parse_effect_localization_document(text)
    if key == "trigger_localization_sample":
        return parse_trigger_localization_document(text)
    if key in _LOCALIZATION_KEYS:
        return parse_localization(text)
    if key == "scripted_trigger":
        return parse_scripted_trigger_document(text)
    if key == "scripted_effect":
        return parse_scripted_effect_document(text)
    if key == "scripted_list_sample":
        return parse_scripted_list_document(text)
    if key in _RELATION_KEYS:
        return parse_scripted_relation_document(text)
    if key in _CASUS_BELLI_KEYS:
        return parse_casus_belli_document(text)
    if key in _PEACE_TREATY_KEYS:
        return parse_peace_treaty_document(text)
    if key in _SUBJECT_TYPE_KEYS:
        return parse_subject_type_document(text)
    if key == "subject_military_stance_sample":
        return parse_subject_military_stance_document(text)
    if key in {"country_interaction_sample", "country_interaction_secondary_sample"}:
        return parse_country_interaction_document(text)
    if key in _CHARACTER_INTERACTION_KEYS:
        return parse_character_interaction_document(text)
    if key in _UNIT_TYPE_KEYS:
        return parse_unit_type_document(text)
    if key in _UNIT_ABILITY_KEYS:
        return parse_unit_ability_document(text)
    if key in _UNIT_CATEGORY_KEYS:
        return parse_unit_category_document(text)
    if key == "government_type_sample":
        return parse_government_type_document(text)
    if key in _GOVERNMENT_REFORM_KEYS:
        return parse_government_reform_document(text)
    if key in _LAW_KEYS:
        return parse_law_document(text)
    if key == "estate_sample":
        return parse_estate_document(text)
    if key in _ESTATE_PRIVILEGE_KEYS:
        return parse_estate_privilege_document(text)
    if key in _PARLIAMENT_TYPE_KEYS:
        return parse_parliament_type_document(text)
    if key in _PARLIAMENT_AGENDA_KEYS:
        return parse_parliament_agenda_document(text)
    if key in _PARLIAMENT_ISSUE_KEYS:
        return parse_parliament_issue_document(text)
    if key in _INSTITUTION_KEYS:
        return parse_institution_document(text)
    if key == "holy_site_type_sample":
        return parse_holy_site_type_document(text)
    if key in _HOLY_SITE_KEYS:
        return parse_holy_site_document(text)
    if key == "societal_value_sample":
        return parse_societal_value_document(text)
    if key in _RELIGIOUS_ASPECT_KEYS:
        return parse_religious_aspect_document(text)
    if key == "religious_faction_sample":
        return parse_religious_faction_document(text)
    if key == "religious_focus_sample":
        return parse_religious_focus_document(text)
    if key in {"religious_school_sample", "religious_school_secondary_sample"}:
        return parse_religious_school_document(text)
    if key in {"religious_figure_sample", "religious_figure_secondary_sample"}:
        return parse_religious_figure_document(text)
    if key == "wargoal_sample":
        return parse_wargoal_document(text)
    if key in {"on_action_sample", "on_action_secondary_sample", "on_action_hardcoded_sample"}:
        return parse_on_action_document(text)
    if key in {"script_value_sample", "script_value_scalar_sample"}:
        return parse_script_value_document(text)
    if key == "building_category_sample":
        return parse_building_category_document(text)
    if key in {"scripted_modifier_info", "scripted_list_info", "culture_info"}:
        return text
    if key in {"building_type_sample", "building_type_secondary_sample"}:
        return parse_building_type_document(text)
    if key in _GOODS_KEYS:
        return parse_goods_document(text)
    if key in _PRICE_KEYS:
        return parse_price_document(text)
    if key == "goods_demand_category_sample":
        return parse_goods_demand_category_document(text)
    if key in _GOODS_DEMAND_KEYS:
        return parse_goods_demand_document(text)
    if key == "production_method_sample":
        return parse_production_method_document(text)
    if key == "employment_system_sample":
        return parse_employment_system_document(text)
    if key in {
        "generic_action_market_sample",
        "generic_action_secondary_sample",
        "generic_action_loan_sample",
    }:
        return parse_generic_action_document(text)
    if key in {
        "attribute_column_default_sample",
        "attribute_column_market_sample",
        "attribute_column_trade_sample",
        "attribute_column_secondary_sample",
        "attribute_column_loan_sample",
    }:
        return parse_attribute_column_document(text)
    if key == "culture_sample":
        return parse_culture_document(text)
    if key in _RELIGION_KEYS:
        return parse_religion_document(text)
    if key == "country_description_category_sample":
        return parse_country_description_category_document(text)
    if key == "setup_country_sample":
        return parse_setup_country_document(text)
    if key in {"gui_sample", "gui_types_sample", "gui_library_sample"}:
        from eu5miner.domains.gui import parse_gui_document

        return parse_gui_document(text)
    if key == "main_menu_scenarios_sample":
        return parse_main_menu_scenarios_document(text)
    if key == "main_menu_country_setup_sample":
        return parse_country_location_document(text)
    if key == "main_menu_location_setup_sample":
        return parse_location_setup_document(text)
    if key == "map_default":
        return parse_default_map_document(text)
    if key == "map_definitions":
        return parse_location_hierarchy_document(text)
    if key == "map_adjacencies":
        return parse_map_adjacencies_document(text)
    if key == "map_ports":
        return parse_map_ports_document(text)
    if key == "dlc_metadata":
        return parse_mod_metadata_document(text)
    return _UNHANDLED


def _assert_non_empty_result(result: Any) -> None:
    if isinstance(result, dict):
        assert result
        return
    if isinstance(result, (list, tuple)):
        assert result
        return
    definitions = getattr(result, "definitions", None)
    if definitions is not None:
        assert definitions
        return
    entries = getattr(result, "entries", None)
    if entries is not None:
        assert entries
        return
    names = getattr(result, "names", None)
    if callable(names):
        assert names()
        return
    assert result is not None


@pytest.mark.timeout(20)
def test_broad_representative_file_matrix_is_accounted_for(game_install: GameInstall) -> None:
    representative_files = game_install.representative_files()
    unhandled_keys: list[str] = []

    for key, path in representative_files.items():
        text = _read_text(path)
        if _is_text_only_key(key):
            assert text.strip(), key
            continue

        parsed = _parse_representative_sample(key, text)
        if parsed is _UNHANDLED:
            unhandled_keys.append(key)
            continue

        _assert_non_empty_result(parsed)

    assert unhandled_keys == []


@pytest.mark.timeout(30)
def test_broad_real_install_helper_integration_sweep(game_install: GameInstall) -> None:
    representative_files = game_install.representative_files()

    customizable_document = parse_customizable_localization_document(
        _read_text(representative_files["customizable_localization_sample"])
    )
    laws_bundle = build_localization_bundle(
        (
            (
                "laws_and_policies_l_english.yml",
                _read_text(representative_files["english_laws_localization"]),
            ),
        )
    )
    customizable_references = tuple(
        reference
        for reference in collect_customizable_localization_references(customizable_document)
        if reference.definition_name == "GetOrderOfChivalry"
    )
    assert customizable_references
    assert find_missing_localization_references(laws_bundle, customizable_references) == ()

    loading_bundle = build_phase_localization_bundle(
        game_install,
        ContentPhase.LOADING_SCREEN,
        "english",
    )
    assert loading_bundle.get_value("LOADING_TIP_0") is not None

    category_usage = build_country_description_category_usage_document(
        parse_country_description_category_document(
            _read_text(representative_files["country_description_category_sample"])
        ),
        parse_setup_country_document(_read_text(representative_files["setup_country_sample"])),
    )
    assert category_usage.assignments

    linked_locations = build_linked_location_document(
        parse_location_hierarchy_document(_read_text(representative_files["map_definitions"])),
        parse_country_location_document(
            _read_text(representative_files["main_menu_country_setup_sample"])
        ),
        parse_location_setup_document(
            _read_text(representative_files["main_menu_location_setup_sample"])
        ),
    )
    assert linked_locations.definitions

    on_action_catalog = build_on_action_catalog_document(
        (
            parse_on_action_document(_read_text(representative_files["on_action_sample"])),
            parse_on_action_document(
                _read_text(representative_files["on_action_secondary_sample"])
            ),
            parse_on_action_document(
                _read_text(representative_files["on_action_hardcoded_sample"])
            ),
        )
    )
    assert on_action_catalog.entries

    law_documents = (
        parse_law_document(_read_text(representative_files["law_sample"])),
        parse_law_document(_read_text(representative_files["law_secondary_sample"])),
        parse_law_document(_read_text(representative_files["law_country_specific_sample"])),
        parse_law_document(_read_text(representative_files["law_io_sample"])),
        parse_law_document(_read_text(representative_files["law_io_secondary_sample"])),
    )
    law_policy_catalog = build_law_policy_catalog(law_documents)
    assert law_policy_catalog.get_law("royal_court_customs_law") is not None
    assert law_policy_catalog.get_policy("forums_of_thought") is not None

    war_flow_catalog = build_war_flow_catalog(
        casus_belli_documents=(
            parse_casus_belli_document(_read_text(representative_files["casus_belli_sample"])),
            parse_casus_belli_document(
                _read_text(representative_files["casus_belli_secondary_sample"])
            ),
            parse_casus_belli_document(
                _read_text(representative_files["casus_belli_subject_sample"])
            ),
        ),
        wargoal_documents=(
            parse_wargoal_document(_read_text(representative_files["wargoal_sample"])),
        ),
        peace_treaty_documents=(
            parse_peace_treaty_document(_read_text(representative_files["peace_treaty_sample"])),
            parse_peace_treaty_document(
                _read_text(representative_files["peace_treaty_secondary_sample"])
            ),
        ),
        subject_type_documents=(
            parse_subject_type_document(_read_text(representative_files["subject_type_sample"])),
            parse_subject_type_document(
                _read_text(representative_files["subject_type_secondary_sample"])
            ),
        ),
    )
    war_flow_report = build_war_flow_report(war_flow_catalog)
    assert war_flow_catalog.casus_belli_definitions
    assert war_flow_catalog.wargoal_definitions
    assert war_flow_report.missing_wargoal_references == ()
    assert war_flow_report.missing_casus_belli_references == ()
    assert war_flow_report.missing_subject_type_references == ()

    common_dir = game_install.phase_dir(ContentPhase.IN_GAME) / "common"
    diplomacy_catalog = build_diplomacy_graph_catalog(
        casus_belli_documents=(
            parse_casus_belli_document("cb_claim_throne = { war_goal_type = sample_goal }\n"),
        ),
        wargoal_documents=(parse_wargoal_document("sample_goal = { type = superiority }\n"),),
        peace_treaty_documents=(),
        subject_type_documents=(
            parse_subject_type_document(
                "fiefdom = { level = 1 }\n"
                "maha_samanta = { level = 1 }\n"
                "pradhana_maha_samanta = { level = 2 }\n"
                "vassal = { level = 1 }\n"
            ),
        ),
        country_interaction_documents=(
            parse_country_interaction_document(
                _read_text(common_dir / "country_interactions" / "break_union.txt")
            ),
            parse_country_interaction_document(
                _read_text(common_dir / "country_interactions" / "samanta_upgrades.txt")
            ),
            parse_country_interaction_document(
                _read_text(common_dir / "country_interactions" / "force_change_court_language.txt")
            ),
        ),
        character_interaction_documents=(
            parse_character_interaction_document(
                _read_text(common_dir / "character_interactions" / "assign_governor.txt")
            ),
        ),
    )
    diplomacy_report = build_diplomacy_graph_report(diplomacy_catalog)
    assert tuple(
        definition.name
        for definition in diplomacy_catalog.get_casus_belli_references_for_country_interaction(
            "break_subject_union"
        )
    ) == ("cb_claim_throne",)
    assert diplomacy_report.missing_casus_belli_references == ()

    government_catalog = build_government_catalog(
        government_type_documents=(
            parse_government_type_document(
                _read_text(representative_files["government_type_sample"])
            ),
        ),
        government_reform_documents=(
            parse_government_reform_document(
                _read_text(representative_files["government_reform_sample"])
            ),
            parse_government_reform_document(
                _read_text(representative_files["government_reform_secondary_sample"])
            ),
        ),
        law_documents=law_documents,
        estate_documents=(
            parse_estate_document(_read_text(representative_files["estate_sample"])),
        ),
        estate_privilege_documents=(
            parse_estate_privilege_document(
                _read_text(representative_files["estate_privilege_sample"])
            ),
            parse_estate_privilege_document(
                _read_text(representative_files["estate_privilege_special_sample"])
            ),
        ),
        parliament_type_documents=(
            parse_parliament_type_document(
                _read_text(representative_files["parliament_type_sample"])
            ),
            parse_parliament_type_document(
                _read_text(representative_files["parliament_type_secondary_sample"])
            ),
        ),
        parliament_agenda_documents=(
            parse_parliament_agenda_document(
                _read_text(representative_files["parliament_agenda_sample"])
            ),
            parse_parliament_agenda_document(
                _read_text(representative_files["parliament_agenda_special_sample"])
            ),
        ),
        parliament_issue_documents=(
            parse_parliament_issue_document(
                _read_text(representative_files["parliament_issue_sample"])
            ),
            parse_parliament_issue_document(
                _read_text(representative_files["parliament_issue_special_sample"])
            ),
        ),
    )
    government_report = build_government_report(government_catalog)
    assert government_catalog.get_default_estate_for_government("monarchy") is not None
    assert government_report.missing_government_type_references == ()

    holy_site_catalog = build_holy_site_catalog(
        (parse_holy_site_type_document(_read_text(representative_files["holy_site_type_sample"])),),
        (
            parse_holy_site_document(_read_text(representative_files["holy_site_sample"])),
            parse_holy_site_document(
                _read_text(representative_files["holy_site_secondary_sample"])
            ),
        ),
    )
    holy_site_report = build_holy_site_report(holy_site_catalog)
    assert holy_site_catalog.get_holy_sites_for_religion("catholic")
    assert holy_site_report.missing_holy_site_type_references == ()

    religion_catalog = build_religion_catalog(
        religion_documents=(
            parse_religion_document(_read_text(representative_files["religion_sample"])),
            parse_religion_document(_read_text(representative_files["religion_secondary_sample"])),
            parse_religion_document(_read_text(representative_files["religion_muslim_sample"])),
            parse_religion_document(_read_text(representative_files["religion_tonal_sample"])),
            parse_religion_document(_read_text(representative_files["religion_dharmic_sample"])),
        ),
        religious_aspect_documents=(
            parse_religious_aspect_document(
                _read_text(representative_files["religious_aspect_sample"])
            ),
        ),
        religious_faction_documents=(
            parse_religious_faction_document(
                _read_text(representative_files["religious_faction_sample"])
            ),
        ),
        religious_focus_documents=(
            parse_religious_focus_document(
                _read_text(representative_files["religious_focus_sample"])
            ),
        ),
        religious_school_documents=tuple(
            parse_religious_school_document(_read_text(path))
            for path in game_install.iter_phase_files(
                ContentPhase.IN_GAME,
                "common/religious_schools",
            )
        ),
        religious_figure_documents=(
            parse_religious_figure_document(
                _read_text(representative_files["religious_figure_sample"])
            ),
            parse_religious_figure_document(
                _read_text(representative_files["religious_figure_secondary_sample"])
            ),
        ),
        holy_site_documents=(
            parse_holy_site_document(_read_text(representative_files["holy_site_sample"])),
            parse_holy_site_document(
                _read_text(representative_files["holy_site_secondary_sample"])
            ),
        ),
    )
    religion_report = build_religion_report(religion_catalog)
    assert religion_catalog.get_religious_schools_for_religion("sunni")
    assert religion_report.missing_religious_school_references == ()

    assert parse_semicolon_csv(_read_text(representative_files["map_adjacencies"]))
    assert parse_metadata_json(_read_text(representative_files["dlc_metadata"]))
