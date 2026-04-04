"""Helpers for CLI system reports over representative install files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eu5miner import ContentPhase
from eu5miner.domains.attribute_columns import parse_attribute_column_document
from eu5miner.domains.diplomacy import (
    build_diplomacy_graph_catalog,
    build_diplomacy_graph_report,
    build_war_flow_catalog,
    build_war_flow_report,
)
from eu5miner.domains.diplomacy.casus_belli import parse_casus_belli_document
from eu5miner.domains.diplomacy.character_interactions import (
    parse_character_interaction_document,
)
from eu5miner.domains.diplomacy.country_interactions import parse_country_interaction_document
from eu5miner.domains.diplomacy.generic_actions import parse_generic_action_document
from eu5miner.domains.diplomacy.peace_treaties import parse_peace_treaty_document
from eu5miner.domains.diplomacy.subject_types import parse_subject_type_document
from eu5miner.domains.diplomacy.wargoals import parse_wargoal_document
from eu5miner.domains.economy import build_market_catalog, build_market_report
from eu5miner.domains.economy.employment_systems import parse_employment_system_document
from eu5miner.domains.economy.goods import parse_goods_document
from eu5miner.domains.economy.goods_demand_categories import (
    parse_goods_demand_category_document,
)
from eu5miner.domains.economy.goods_demands import parse_goods_demand_document
from eu5miner.domains.economy.prices import parse_price_document
from eu5miner.domains.economy.production_methods import parse_production_method_document
from eu5miner.domains.frontend_content import (
    build_phase_localization_bundle,
    parse_main_menu_scenarios_document,
)
from eu5miner.domains.government import build_government_catalog, build_government_report
from eu5miner.domains.government.estate_privileges import parse_estate_privilege_document
from eu5miner.domains.government.estates import parse_estate_document
from eu5miner.domains.government.government_reforms import parse_government_reform_document
from eu5miner.domains.government.government_types import parse_government_type_document
from eu5miner.domains.government.laws import parse_law_document
from eu5miner.domains.government.parliament_agendas import parse_parliament_agenda_document
from eu5miner.domains.government.parliament_issues import parse_parliament_issue_document
from eu5miner.domains.government.parliament_types import parse_parliament_type_document
from eu5miner.domains.gui import parse_gui_document
from eu5miner.domains.institutions import parse_institution_document
from eu5miner.domains.localization import (
    build_localization_bundle,
    collect_customizable_localization_references,
    collect_effect_localization_references,
    collect_trigger_localization_references,
    find_missing_localization_references,
    parse_customizable_localization_document,
    parse_effect_localization_document,
    parse_trigger_localization_document,
)
from eu5miner.domains.map import (
    build_linked_location_document,
    parse_country_location_document,
    parse_default_map_document,
    parse_location_hierarchy_document,
    parse_location_setup_document,
    parse_map_adjacencies_document,
    parse_map_ports_document,
)
from eu5miner.domains.religion import build_religion_catalog, build_religion_report
from eu5miner.domains.religion.holy_site_types import parse_holy_site_type_document
from eu5miner.domains.religion.holy_sites import parse_holy_site_document
from eu5miner.domains.religion.religions import parse_religion_document
from eu5miner.domains.religion.religious_aspects import parse_religious_aspect_document
from eu5miner.domains.religion.religious_factions import parse_religious_faction_document
from eu5miner.domains.religion.religious_figures import parse_religious_figure_document
from eu5miner.domains.religion.religious_focuses import parse_religious_focus_document
from eu5miner.domains.religion.religious_schools import parse_religious_school_document
from eu5miner.domains.units import (
    parse_unit_ability_document,
    parse_unit_category_document,
    parse_unit_type_document,
)
from eu5miner.source import GameInstall


@dataclass(frozen=True)
class CliSystemInfo:
    name: str
    description: str


@dataclass(frozen=True)
class CliSystemReport:
    name: str
    description: str
    representative_keys: tuple[str, ...]
    summary_lines: tuple[str, ...]


SYSTEMS: tuple[CliSystemInfo, ...] = (
    CliSystemInfo(
        name="economy",
        description="Goods, prices, production, demand, and market helper coverage.",
    ),
    CliSystemInfo(
        name="diplomacy",
        description="War-flow, diplomacy graph, and unit-family coverage.",
    ),
    CliSystemInfo(
        name="government",
        description="Government, law, estate, parliament, and institution coverage.",
    ),
    CliSystemInfo(
        name="religion",
        description="Religion, holy-site, and religious helper coverage.",
    ),
    CliSystemInfo(
        name="interface",
        description="Localization, GUI, and frontend-content coverage.",
    ),
    CliSystemInfo(
        name="map",
        description="Map text, map CSV, and linked setup-location coverage.",
    ),
)


def list_systems() -> tuple[CliSystemInfo, ...]:
    return SYSTEMS


def build_system_report(
    install: GameInstall,
    system: str,
    *,
    language: str = "english",
) -> CliSystemReport:
    representative_files = install.representative_files()

    if system == "economy":
        return _build_economy_report(representative_files)
    if system == "diplomacy":
        return _build_diplomacy_report(representative_files)
    if system == "government":
        return _build_government_report(representative_files)
    if system == "religion":
        return _build_religion_report(representative_files)
    if system == "interface":
        return _build_interface_report(install, representative_files, language)
    if system == "map":
        return _build_map_report(representative_files)

    valid_systems = ", ".join(info.name for info in SYSTEMS)
    raise KeyError(f"Unknown system '{system}'. Valid systems: {valid_systems}")


def format_system_report(report: CliSystemReport) -> str:
    lines = [
        f"System report: {report.name}",
        f"Description: {report.description}",
        "Representative files:",
        *(f"- {key}" for key in report.representative_keys),
        "Summary:",
        *(f"- {line}" for line in report.summary_lines),
    ]
    return "\n".join(lines)


def _build_economy_report(representative_files: dict[str, Path]) -> CliSystemReport:
    representative_keys = (
        "goods_sample",
        "goods_secondary_sample",
        "price_sample",
        "price_secondary_sample",
        "goods_demand_category_sample",
        "goods_demand_sample",
        "goods_demand_secondary_sample",
        "goods_demand_tertiary_sample",
        "production_method_sample",
        "employment_system_sample",
        "generic_action_market_sample",
        "generic_action_secondary_sample",
        "generic_action_loan_sample",
        "attribute_column_default_sample",
        "attribute_column_market_sample",
        "attribute_column_trade_sample",
        "attribute_column_secondary_sample",
        "attribute_column_loan_sample",
    )
    goods_documents = tuple(
        parse_goods_document(_read_text(representative_files[key]))
        for key in ("goods_sample", "goods_secondary_sample")
    )
    price_documents = tuple(
        parse_price_document(_read_text(representative_files[key]))
        for key in ("price_sample", "price_secondary_sample")
    )
    goods_demand_category_document = parse_goods_demand_category_document(
        _read_text(representative_files["goods_demand_category_sample"])
    )
    goods_demand_documents = tuple(
        parse_goods_demand_document(_read_text(representative_files[key]))
        for key in (
            "goods_demand_sample",
            "goods_demand_secondary_sample",
            "goods_demand_tertiary_sample",
        )
    )
    production_method_document = parse_production_method_document(
        _read_text(representative_files["production_method_sample"])
    )
    employment_system_document = parse_employment_system_document(
        _read_text(representative_files["employment_system_sample"])
    )
    generic_action_documents = tuple(
        parse_generic_action_document(_read_text(representative_files[key]))
        for key in (
            "generic_action_market_sample",
            "generic_action_secondary_sample",
            "generic_action_loan_sample",
        )
    )
    attribute_column_documents = tuple(
        parse_attribute_column_document(_read_text(representative_files[key]))
        for key in (
            "attribute_column_default_sample",
            "attribute_column_market_sample",
            "attribute_column_trade_sample",
            "attribute_column_secondary_sample",
            "attribute_column_loan_sample",
        )
    )
    market_catalog = build_market_catalog(
        goods_documents=goods_documents,
        price_documents=price_documents,
        generic_action_documents=generic_action_documents,
        attribute_column_documents=attribute_column_documents,
    )
    market_report = build_market_report(market_catalog)

    return CliSystemReport(
        name="economy",
        description=_description_for("economy"),
        representative_keys=representative_keys,
        summary_lines=(
            f"goods definitions: {len(market_catalog.goods_definitions)}",
            f"price definitions: {len(market_catalog.price_definitions)}",
            f"goods demand categories: {len(goods_demand_category_document.definitions)}",
            "goods demand definitions: "
            f"{sum(len(document.definitions) for document in goods_demand_documents)}",
            f"production method definitions: {len(production_method_document.definitions)}",
            f"employment system definitions: {len(employment_system_document.definitions)}",
            f"market actions: {len(market_catalog.get_market_actions())}",
            f"attribute column groups: {len(market_catalog.attribute_group_definitions)}",
            f"priced goods: {len(market_report.priced_goods)}",
            f"sample priced goods: {_preview(market_report.priced_goods)}",
        ),
    )


def _build_diplomacy_report(representative_files: dict[str, Path]) -> CliSystemReport:
    representative_keys = (
        "casus_belli_sample",
        "casus_belli_secondary_sample",
        "casus_belli_subject_sample",
        "casus_belli_religious_sample",
        "casus_belli_trade_sample",
        "wargoal_sample",
        "peace_treaty_sample",
        "peace_treaty_secondary_sample",
        "peace_treaty_special_sample",
        "subject_type_sample",
        "subject_type_secondary_sample",
        "subject_type_colonial_sample",
        "subject_type_hre_sample",
        "subject_type_special_sample",
        "country_interaction_sample",
        "country_interaction_secondary_sample",
        "character_interaction_sample",
        "character_interaction_secondary_sample",
        "character_interaction_ui_sample",
        "unit_type_sample",
        "unit_type_secondary_sample",
        "unit_ability_sample",
        "unit_ability_secondary_sample",
        "unit_category_sample",
        "unit_category_secondary_sample",
    )
    casus_belli_documents = tuple(
        parse_casus_belli_document(_read_text(representative_files[key]))
        for key in (
            "casus_belli_sample",
            "casus_belli_secondary_sample",
            "casus_belli_subject_sample",
            "casus_belli_religious_sample",
            "casus_belli_trade_sample",
        )
    )
    wargoal_documents = (
        parse_wargoal_document(_read_text(representative_files["wargoal_sample"])),
    )
    peace_treaty_documents = tuple(
        parse_peace_treaty_document(_read_text(representative_files[key]))
        for key in (
            "peace_treaty_sample",
            "peace_treaty_secondary_sample",
            "peace_treaty_special_sample",
        )
    )
    subject_type_documents = tuple(
        parse_subject_type_document(_read_text(representative_files[key]))
        for key in (
            "subject_type_sample",
            "subject_type_secondary_sample",
            "subject_type_colonial_sample",
            "subject_type_hre_sample",
            "subject_type_special_sample",
        )
    )
    country_interaction_documents = tuple(
        parse_country_interaction_document(_read_text(representative_files[key]))
        for key in ("country_interaction_sample", "country_interaction_secondary_sample")
    )
    character_interaction_documents = tuple(
        parse_character_interaction_document(_read_text(representative_files[key]))
        for key in (
            "character_interaction_sample",
            "character_interaction_secondary_sample",
            "character_interaction_ui_sample",
        )
    )
    war_flow_catalog = build_war_flow_catalog(
        casus_belli_documents=casus_belli_documents,
        wargoal_documents=wargoal_documents,
        peace_treaty_documents=peace_treaty_documents,
        subject_type_documents=subject_type_documents,
    )
    war_flow_report = build_war_flow_report(war_flow_catalog)
    diplomacy_catalog = build_diplomacy_graph_catalog(
        casus_belli_documents=casus_belli_documents,
        wargoal_documents=wargoal_documents,
        peace_treaty_documents=peace_treaty_documents,
        subject_type_documents=subject_type_documents,
        country_interaction_documents=country_interaction_documents,
        character_interaction_documents=character_interaction_documents,
    )
    diplomacy_report = build_diplomacy_graph_report(diplomacy_catalog)
    unit_type_documents = tuple(
        parse_unit_type_document(_read_text(representative_files[key]))
        for key in ("unit_type_sample", "unit_type_secondary_sample")
    )
    unit_ability_documents = tuple(
        parse_unit_ability_document(_read_text(representative_files[key]))
        for key in ("unit_ability_sample", "unit_ability_secondary_sample")
    )
    unit_category_documents = tuple(
        parse_unit_category_document(_read_text(representative_files[key]))
        for key in ("unit_category_sample", "unit_category_secondary_sample")
    )

    return CliSystemReport(
        name="diplomacy",
        description=_description_for("diplomacy"),
        representative_keys=representative_keys,
        summary_lines=(
            f"casus belli definitions: {len(war_flow_catalog.casus_belli_definitions)}",
            f"wargoal definitions: {len(war_flow_catalog.wargoal_definitions)}",
            f"peace treaty definitions: {len(war_flow_catalog.peace_treaty_definitions)}",
            f"subject type definitions: {len(war_flow_catalog.subject_type_definitions)}",
            "country interaction definitions: "
            f"{len(diplomacy_catalog.country_interaction_definitions)}",
            "character interaction definitions: "
            f"{len(diplomacy_catalog.character_interaction_definitions)}",
            f"missing wargoal references: {len(war_flow_report.missing_wargoal_references)}",
            "missing casus belli references: "
            f"{len(diplomacy_report.missing_casus_belli_references)}",
            "missing subject type references: "
            f"{len(diplomacy_report.missing_subject_type_references)}",
            "missing country interaction references: "
            f"{len(diplomacy_report.missing_country_interaction_references)}",
            "unit type definitions: "
            f"{sum(len(document.definitions) for document in unit_type_documents)}",
            "unit ability definitions: "
            f"{sum(len(document.definitions) for document in unit_ability_documents)}",
            "unit category definitions: "
            f"{sum(len(document.definitions) for document in unit_category_documents)}",
        ),
    )


def _build_government_report(representative_files: dict[str, Path]) -> CliSystemReport:
    representative_keys = (
        "government_type_sample",
        "government_reform_sample",
        "government_reform_secondary_sample",
        "government_reform_special_sample",
        "law_sample",
        "law_secondary_sample",
        "law_country_specific_sample",
        "law_io_sample",
        "law_io_secondary_sample",
        "estate_sample",
        "estate_privilege_sample",
        "estate_privilege_secondary_sample",
        "estate_privilege_special_sample",
        "parliament_type_sample",
        "parliament_type_secondary_sample",
        "parliament_agenda_sample",
        "parliament_agenda_secondary_sample",
        "parliament_agenda_special_sample",
        "parliament_issue_sample",
        "parliament_issue_secondary_sample",
        "parliament_issue_special_sample",
        "institution_sample",
        "institution_secondary_sample",
    )
    government_catalog = build_government_catalog(
        government_type_documents=(
            parse_government_type_document(
                _read_text(representative_files["government_type_sample"])
            ),
        ),
        government_reform_documents=tuple(
            parse_government_reform_document(_read_text(representative_files[key]))
            for key in (
                "government_reform_sample",
                "government_reform_secondary_sample",
                "government_reform_special_sample",
            )
        ),
        law_documents=tuple(
            parse_law_document(_read_text(representative_files[key]))
            for key in (
                "law_sample",
                "law_secondary_sample",
                "law_country_specific_sample",
                "law_io_sample",
                "law_io_secondary_sample",
            )
        ),
        estate_documents=(
            parse_estate_document(_read_text(representative_files["estate_sample"])),
        ),
        estate_privilege_documents=tuple(
            parse_estate_privilege_document(_read_text(representative_files[key]))
            for key in (
                "estate_privilege_sample",
                "estate_privilege_secondary_sample",
                "estate_privilege_special_sample",
            )
        ),
        parliament_type_documents=tuple(
            parse_parliament_type_document(_read_text(representative_files[key]))
            for key in ("parliament_type_sample", "parliament_type_secondary_sample")
        ),
        parliament_agenda_documents=tuple(
            parse_parliament_agenda_document(_read_text(representative_files[key]))
            for key in (
                "parliament_agenda_sample",
                "parliament_agenda_secondary_sample",
                "parliament_agenda_special_sample",
            )
        ),
        parliament_issue_documents=tuple(
            parse_parliament_issue_document(_read_text(representative_files[key]))
            for key in (
                "parliament_issue_sample",
                "parliament_issue_secondary_sample",
                "parliament_issue_special_sample",
            )
        ),
    )
    government_report = build_government_report(government_catalog)
    institution_documents = tuple(
        parse_institution_document(_read_text(representative_files[key]))
        for key in ("institution_sample", "institution_secondary_sample")
    )
    policy_count = sum(
        len(definition.policies)
        for definition in government_catalog.law_policy_catalog.law_definitions
    )

    return CliSystemReport(
        name="government",
        description=_description_for("government"),
        representative_keys=representative_keys,
        summary_lines=(
            f"government type definitions: {len(government_catalog.government_type_definitions)}",
            "government reform definitions: "
            f"{len(government_catalog.government_reform_definitions)}",
            f"law definitions: {len(government_catalog.law_definitions)}",
            f"law policy definitions: {policy_count}",
            f"estate definitions: {len(government_catalog.estate_definitions)}",
            f"estate privilege definitions: {len(government_catalog.estate_privilege_definitions)}",
            f"parliament type definitions: {len(government_catalog.parliament_type_definitions)}",
            "parliament agenda definitions: "
            f"{len(government_catalog.parliament_agenda_definitions)}",
            f"parliament issue definitions: {len(government_catalog.parliament_issue_definitions)}",
            "institution definitions: "
            f"{sum(len(document.definitions) for document in institution_documents)}",
            "missing government type references: "
            f"{len(government_report.missing_government_type_references)}",
            f"missing estate references: {len(government_report.missing_estate_references)}",
        ),
    )


def _build_religion_report(representative_files: dict[str, Path]) -> CliSystemReport:
    representative_keys = (
        "religion_sample",
        "religion_secondary_sample",
        "religion_muslim_sample",
        "religion_tonal_sample",
        "religion_dharmic_sample",
        "religious_aspect_sample",
        "religious_aspect_secondary_sample",
        "religious_faction_sample",
        "religious_focus_sample",
        "religious_school_sample",
        "religious_school_secondary_sample",
        "religious_figure_sample",
        "religious_figure_secondary_sample",
        "holy_site_type_sample",
        "holy_site_sample",
        "holy_site_secondary_sample",
    )
    religion_catalog = build_religion_catalog(
        religion_documents=tuple(
            parse_religion_document(_read_text(representative_files[key]))
            for key in (
                "religion_sample",
                "religion_secondary_sample",
                "religion_muslim_sample",
                "religion_tonal_sample",
                "religion_dharmic_sample",
            )
        ),
        religious_aspect_documents=tuple(
            parse_religious_aspect_document(_read_text(representative_files[key]))
            for key in ("religious_aspect_sample", "religious_aspect_secondary_sample")
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
            parse_religious_school_document(_read_text(representative_files[key]))
            for key in ("religious_school_sample", "religious_school_secondary_sample")
        ),
        religious_figure_documents=tuple(
            parse_religious_figure_document(_read_text(representative_files[key]))
            for key in ("religious_figure_sample", "religious_figure_secondary_sample")
        ),
        holy_site_documents=tuple(
            parse_holy_site_document(_read_text(representative_files[key]))
            for key in ("holy_site_sample", "holy_site_secondary_sample")
        ),
    )
    religion_report = build_religion_report(religion_catalog)
    holy_site_type_documents = (
        parse_holy_site_type_document(_read_text(representative_files["holy_site_type_sample"])),
    )

    return CliSystemReport(
        name="religion",
        description=_description_for("religion"),
        representative_keys=representative_keys,
        summary_lines=(
            f"religion definitions: {len(religion_catalog.religion_definitions)}",
            f"religious aspect definitions: {len(religion_catalog.religious_aspect_definitions)}",
            f"religious faction definitions: {len(religion_catalog.religious_faction_definitions)}",
            f"religious focus definitions: {len(religion_catalog.religious_focus_definitions)}",
            f"religious school definitions: {len(religion_catalog.religious_school_definitions)}",
            f"religious figure definitions: {len(religion_catalog.religious_figure_definitions)}",
            "holy site type definitions: "
            f"{sum(len(document.definitions) for document in holy_site_type_documents)}",
            f"holy site definitions: {len(religion_catalog.holy_site_definitions)}",
            "missing faction references: "
            f"{len(religion_report.missing_religious_faction_references)}",
            f"missing focus references: {len(religion_report.missing_religious_focus_references)}",
            "missing school references: "
            f"{len(religion_report.missing_religious_school_references)}",
        ),
    )


def _build_interface_report(
    install: GameInstall,
    representative_files: dict[str, Path],
    language: str,
) -> CliSystemReport:
    representative_keys = (
        "customizable_localization_sample",
        "effect_localization_sample",
        "trigger_localization_sample",
        "english_laws_localization",
        "english_effects_localization",
        "english_triggers_localization",
        "gui_sample",
        "gui_types_sample",
        "gui_library_sample",
        "main_menu_scenarios_sample",
        "loading_screen_localization_sample",
    )
    customizable_document = parse_customizable_localization_document(
        _read_text(representative_files["customizable_localization_sample"])
    )
    effect_document = parse_effect_localization_document(
        _read_text(representative_files["effect_localization_sample"])
    )
    trigger_document = parse_trigger_localization_document(
        _read_text(representative_files["trigger_localization_sample"])
    )
    laws_bundle = build_localization_bundle(
        (
            (
                "laws_and_policies_l_english.yml",
                _read_text(representative_files["english_laws_localization"]),
            ),
        )
    )
    effects_bundle = build_localization_bundle(
        (
            (
                "effects_l_english.yml",
                _read_text(representative_files["english_effects_localization"]),
            ),
        )
    )
    triggers_bundle = build_localization_bundle(
        (
            (
                "triggers_l_english.yml",
                _read_text(representative_files["english_triggers_localization"]),
            ),
        )
    )
    gui_documents = tuple(
        parse_gui_document(_read_text(representative_files[key]))
        for key in ("gui_sample", "gui_types_sample", "gui_library_sample")
    )
    scenario_document = parse_main_menu_scenarios_document(
        _read_text(representative_files["main_menu_scenarios_sample"])
    )
    loading_bundle = build_phase_localization_bundle(install, ContentPhase.LOADING_SCREEN, language)
    missing_customizable = find_missing_localization_references(
        laws_bundle,
        collect_customizable_localization_references(customizable_document),
    )
    missing_effect = find_missing_localization_references(
        effects_bundle,
        collect_effect_localization_references(effect_document),
    )
    missing_trigger = find_missing_localization_references(
        triggers_bundle,
        collect_trigger_localization_references(trigger_document),
    )
    gui_typed_definition_count = sum(
        len(group.definitions) for document in gui_documents for group in document.type_groups
    )
    gui_root_definition_count = sum(len(document.root_definitions) for document in gui_documents)

    return CliSystemReport(
        name="interface",
        description=_description_for("interface"),
        representative_keys=representative_keys,
        summary_lines=(
            f"customizable localization definitions: {len(customizable_document.definitions)}",
            f"effect localization definitions: {len(effect_document.definitions)}",
            f"trigger localization definitions: {len(trigger_document.definitions)}",
            f"laws localization keys: {len(laws_bundle.entries)}",
            f"effects localization keys: {len(effects_bundle.entries)}",
            f"triggers localization keys: {len(triggers_bundle.entries)}",
            f"missing customizable localization references: {len(missing_customizable)}",
            f"missing effect localization references: {len(missing_effect)}",
            f"missing trigger localization references: {len(missing_trigger)}",
            f"GUI constants: {sum(len(document.constants) for document in gui_documents)}",
            f"GUI templates: {sum(len(document.templates) for document in gui_documents)}",
            f"GUI type groups: {sum(len(document.type_groups) for document in gui_documents)}",
            f"GUI typed definitions: {gui_typed_definition_count}",
            f"GUI root definitions: {gui_root_definition_count}",
            f"main menu scenarios: {len(scenario_document.definitions)}",
            f"loading-screen localization keys ({language}): {len(loading_bundle.entries)}",
        ),
    )


def _build_map_report(representative_files: dict[str, Path]) -> CliSystemReport:
    representative_keys = (
        "map_default",
        "map_definitions",
        "map_adjacencies",
        "map_ports",
        "main_menu_country_setup_sample",
        "main_menu_location_setup_sample",
    )
    default_map_document = parse_default_map_document(
        _read_text(representative_files["map_default"])
    )
    hierarchy_document = parse_location_hierarchy_document(
        _read_text(representative_files["map_definitions"])
    )
    country_document = parse_country_location_document(
        _read_text(representative_files["main_menu_country_setup_sample"])
    )
    setup_document = parse_location_setup_document(
        _read_text(representative_files["main_menu_location_setup_sample"])
    )
    linked_document = build_linked_location_document(
        hierarchy_document,
        country_document,
        setup_document,
    )
    adjacency_document = parse_map_adjacencies_document(
        _read_text(representative_files["map_adjacencies"])
    )
    ports_document = parse_map_ports_document(_read_text(representative_files["map_ports"]))
    referenced_file_count = sum(
        1 for value in default_map_document.referenced_files.as_dict().values() if value is not None
    )
    linked_with_setup_count = sum(
        1 for definition in linked_document.definitions if definition.has_location_setup
    )
    capital_count = sum(1 for definition in linked_document.definitions if definition.capital_of)

    return CliSystemReport(
        name="map",
        description=_description_for("map"),
        representative_keys=representative_keys,
        summary_lines=(
            f"default.map referenced files: {referenced_file_count}",
            f"location hierarchy definitions: {len(hierarchy_document.definitions)}",
            f"country location definitions: {len(country_document.definitions)}",
            f"location setup definitions: {len(setup_document.definitions)}",
            f"linked locations: {len(linked_document.definitions)}",
            f"linked locations with setup data: {linked_with_setup_count}",
            f"locations marked as capitals: {capital_count}",
            f"map adjacencies: {len(adjacency_document.definitions)}",
            f"map ports: {len(ports_document.definitions)}",
        ),
    )


def _description_for(system: str) -> str:
    for info in SYSTEMS:
        if info.name == system:
            return info.description
    raise KeyError(system)


def _preview(values: tuple[str, ...], *, limit: int = 5) -> str:
    if not values:
        return "(none)"
    preview_values = values[:limit]
    text = ", ".join(preview_values)
    if len(values) > limit:
        return f"{text}, ..."
    return text


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")
