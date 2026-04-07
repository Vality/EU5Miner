"""Stable read-only facade for install inspection, reports, and entity browsing."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from eu5miner.domains.attribute_columns import parse_attribute_column_document
from eu5miner.domains.diplomacy import (
    build_diplomacy_graph_catalog,
    build_diplomacy_graph_report,
    build_war_flow_catalog,
    build_war_flow_report,
    collect_casus_belli_references,
    parse_casus_belli_document,
    parse_character_interaction_document,
    parse_country_interaction_document,
    parse_generic_action_document,
    parse_peace_treaty_document,
    parse_subject_type_document,
    parse_wargoal_document,
)
from eu5miner.domains.economy import (
    build_market_catalog,
    build_market_report,
    parse_employment_system_document,
    parse_goods_demand_category_document,
    parse_goods_demand_document,
    parse_goods_document,
    parse_price_document,
    parse_production_method_document,
)
from eu5miner.domains.frontend_content import (
    build_phase_localization_bundle,
    parse_main_menu_scenarios_document,
)
from eu5miner.domains.government import (
    build_government_catalog,
    build_government_report,
    parse_estate_document,
    parse_estate_privilege_document,
    parse_government_reform_document,
    parse_government_type_document,
    parse_law_document,
    parse_parliament_agenda_document,
    parse_parliament_issue_document,
    parse_parliament_type_document,
)
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
from eu5miner.domains.religion import (
    build_religion_catalog,
    build_religion_report,
    parse_holy_site_document,
    parse_holy_site_type_document,
    parse_religion_document,
    parse_religious_aspect_document,
    parse_religious_faction_document,
    parse_religious_figure_document,
    parse_religious_focus_document,
    parse_religious_school_document,
)
from eu5miner.domains.units import (
    parse_unit_ability_document,
    parse_unit_category_document,
    parse_unit_type_document,
)
from eu5miner.source import ContentPhase, GameInstall
from eu5miner.vfs import SourceKind, VirtualFilesystem

BrowseValue = str | int | float | bool | tuple[str, ...]


@dataclass(frozen=True)
class InstallPhaseRoot:
    phase: ContentPhase
    path: Path


@dataclass(frozen=True)
class InstallSourceSummary:
    name: str
    kind: SourceKind
    root: Path
    priority: int
    replace_paths: tuple[str, ...]


@dataclass(frozen=True)
class InstallSummary:
    root: Path
    game_dir: Path
    dlc_dir: Path
    mod_dir: Path
    phase_roots: tuple[InstallPhaseRoot, ...]
    sources: tuple[InstallSourceSummary, ...]


@dataclass(frozen=True)
class SystemInfo:
    name: str
    description: str


@dataclass(frozen=True)
class SystemReport:
    name: str
    description: str
    representative_keys: tuple[str, ...]
    summary_lines: tuple[str, ...]


@dataclass(frozen=True)
class EntitySystemInfo:
    name: str
    description: str
    primary_entity_kind: str


@dataclass(frozen=True)
class EntitySummary:
    system: str
    entity_kind: str
    name: str
    group: str | None
    description: str | None


@dataclass(frozen=True)
class EntityField:
    name: str
    value: BrowseValue


@dataclass(frozen=True)
class EntityReference:
    role: str
    system: str
    entity_kind: str
    target_name: str


@dataclass(frozen=True)
class EntityDetail:
    summary: EntitySummary
    fields: tuple[EntityField, ...]
    references: tuple[EntityReference, ...]


@dataclass(frozen=True)
class _EntityQueryCacheKey:
    install_root: Path
    system: str
    mod_roots: tuple[Path, ...]


@dataclass(frozen=True)
class _EntityQueryIndex:
    details: tuple[EntityDetail, ...]
    summaries: tuple[EntitySummary, ...]
    by_name: dict[str, EntityDetail]


@dataclass(frozen=True)
class _EntitySystemSourceRoot:
    phase: ContentPhase
    relative_root: Path


_SUPPORTED_SYSTEMS: tuple[SystemInfo, ...] = (
    SystemInfo(
        name="economy",
        description="Goods, prices, production, demand, and market helper coverage.",
    ),
    SystemInfo(
        name="diplomacy",
        description="War-flow, diplomacy graph, and unit-family coverage.",
    ),
    SystemInfo(
        name="government",
        description="Government, law, estate, parliament, and institution coverage.",
    ),
    SystemInfo(
        name="religion",
        description="Religion, holy-site, and religious helper coverage.",
    ),
    SystemInfo(
        name="interface",
        description="Localization, GUI, and frontend-content coverage.",
    ),
    SystemInfo(
        name="map",
        description="Map text, map CSV, and linked setup-location coverage.",
    ),
)

_BROWSABLE_SYSTEMS: tuple[EntitySystemInfo, ...] = (
    EntitySystemInfo(
        name="economy",
        description="Browse goods definitions with market-facing fields and related good links.",
        primary_entity_kind="good",
    ),
    EntitySystemInfo(
        name="diplomacy",
        description=(
            "Browse casus belli definitions with linked wargoals, peace treaties, "
            "and country interactions."
        ),
        primary_entity_kind="casus_belli",
    ),
    EntitySystemInfo(
        name="government",
        description="Browse government types with linked reforms, laws, and default estates.",
        primary_entity_kind="government_type",
    ),
    EntitySystemInfo(
        name="religion",
        description=(
            "Browse religions with linked aspects, factions, focuses, schools, "
            "figures, and holy sites."
        ),
        primary_entity_kind="religion",
    ),
    EntitySystemInfo(
        name="map",
        description="Browse linked locations merged from map hierarchy and main-menu setup data.",
        primary_entity_kind="location",
    ),
)

_ENTITY_QUERY_CACHE: dict[_EntityQueryCacheKey, _EntityQueryIndex] = {}

_ENTITY_SYSTEM_SOURCE_ROOTS: dict[str, tuple[_EntitySystemSourceRoot, ...]] = {
    "economy": (
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "goods"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "prices"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "generic_actions"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "attribute_columns"),
    ),
    "diplomacy": (
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "casus_belli"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "wargoals"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "peace_treaties"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "subject_types"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "country_interactions"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "character_interactions"),
    ),
    "government": (
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "government_types"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "government_reforms"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "laws"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "estates"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "estate_privileges"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "parliament_types"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "parliament_agendas"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "parliament_issues"),
    ),
    "religion": (
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "religions"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "religious_aspects"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "religious_factions"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "religious_focuses"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "religious_schools"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "religious_figures"),
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("common") / "holy_sites"),
    ),
    "map": (
        _EntitySystemSourceRoot(ContentPhase.IN_GAME, Path("map_data") / "definitions.txt"),
        _EntitySystemSourceRoot(
            ContentPhase.MAIN_MENU,
            Path("setup") / "start" / "10_countries.txt",
        ),
        _EntitySystemSourceRoot(
            ContentPhase.MAIN_MENU,
            Path("setup") / "start" / "21_locations.txt",
        ),
    ),
}


def inspect_install(
    root: str | Path | None = None,
    *,
    mod_roots: Sequence[Path] | None = None,
) -> InstallSummary:
    install = GameInstall.discover(root)
    return summarize_install(install, mod_roots=mod_roots)


def summarize_install(
    install: GameInstall,
    *,
    mod_roots: Sequence[Path] | None = None,
) -> InstallSummary:
    vfs = VirtualFilesystem.from_install(
        install,
        mod_roots=list(mod_roots) if mod_roots is not None else None,
    )
    return InstallSummary(
        root=install.root,
        game_dir=install.game_dir,
        dlc_dir=install.dlc_dir,
        mod_dir=install.mod_dir,
        phase_roots=tuple(
            InstallPhaseRoot(phase=phase, path=install.phase_dir(phase))
            for phase in ContentPhase
        ),
        sources=tuple(
            InstallSourceSummary(
                name=source.name,
                kind=source.kind,
                root=source.root,
                priority=source.priority,
                replace_paths=tuple(rule.raw_path for rule in source.replace_rules),
            )
            for source in vfs.sources
        ),
    )


def format_install_summary(summary: InstallSummary) -> str:
    lines = [
        f"Install root: {summary.root}",
        f"Game dir: {summary.game_dir}",
        f"DLC dir: {summary.dlc_dir}",
        f"Mod dir: {summary.mod_dir}",
        "Phase roots:",
        *(f"- {phase_root.phase.value}: {phase_root.path}" for phase_root in summary.phase_roots),
        "Sources:",
        *(
            f"- {source.kind.value}:{source.name} priority={source.priority} root={source.root}"
            for source in summary.sources
        ),
    ]
    return "\n".join(lines)


def list_supported_systems() -> tuple[SystemInfo, ...]:
    return _SUPPORTED_SYSTEMS


def list_entity_systems() -> tuple[EntitySystemInfo, ...]:
    return _BROWSABLE_SYSTEMS


def list_system_entities(
    install: GameInstall,
    system: str,
    *,
    mod_roots: Sequence[Path] | None = None,
) -> tuple[EntitySummary, ...]:
    return _load_system_entity_index(install, system, mod_roots).summaries


def invalidate_system_entity_cache(
    install: GameInstall | str | Path,
    system: str,
    *,
    mod_root: Path | None = None,
) -> int:
    """Invalidate cached entity queries for one system and install context."""

    _entity_description_for(system)
    install_root = _resolved_install_root(install)
    resolved_mod_root = mod_root.resolve() if mod_root is not None else None

    return _invalidate_entity_query_cache(
        lambda cache_key: cache_key.install_root == install_root
        and cache_key.system == system
        and (resolved_mod_root is None or resolved_mod_root in cache_key.mod_roots)
    )


def get_system_entity(
    install: GameInstall,
    system: str,
    name: str,
    *,
    mod_roots: Sequence[Path] | None = None,
) -> EntityDetail:
    detail = _load_system_entity_index(install, system, mod_roots).by_name.get(name)
    if detail is not None:
        return detail

    raise KeyError(f"Unknown entity '{name}' for system '{system}'")


def get_system_report(
    install: GameInstall,
    system: str,
    *,
    language: str = "english",
) -> SystemReport:
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

    valid_systems = ", ".join(info.name for info in _SUPPORTED_SYSTEMS)
    raise KeyError(f"Unknown system '{system}'. Valid systems: {valid_systems}")


def format_system_report(report: SystemReport) -> str:
    lines = [
        f"System report: {report.name}",
        f"Description: {report.description}",
        "Representative files:",
        *(f"- {key}" for key in report.representative_keys),
        "Summary:",
        *(f"- {line}" for line in report.summary_lines),
    ]
    return "\n".join(lines)


def _build_economy_report(representative_files: dict[str, Path]) -> SystemReport:
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

    return SystemReport(
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


def _build_diplomacy_report(representative_files: dict[str, Path]) -> SystemReport:
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

    return SystemReport(
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


def _build_government_report(representative_files: dict[str, Path]) -> SystemReport:
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
            parse_government_type_document(_read_text(representative_files["government_type_sample"])),
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

    return SystemReport(
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


def _build_religion_report(representative_files: dict[str, Path]) -> SystemReport:
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
            parse_religious_faction_document(_read_text(representative_files["religious_faction_sample"])),
        ),
        religious_focus_documents=(
            parse_religious_focus_document(_read_text(representative_files["religious_focus_sample"])),
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

    return SystemReport(
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
) -> SystemReport:
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

    return SystemReport(
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


def _build_map_report(representative_files: dict[str, Path]) -> SystemReport:
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

    return SystemReport(
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
    for info in _SUPPORTED_SYSTEMS:
        if info.name == system:
            return info.description
    raise KeyError(system)


def _entity_description_for(system: str) -> str:
    for info in _BROWSABLE_SYSTEMS:
        if info.name == system:
            return info.description
    valid_systems = ", ".join(info.name for info in _BROWSABLE_SYSTEMS)
    raise KeyError(f"Unknown entity system '{system}'. Valid systems: {valid_systems}")


def _load_system_entity_details(
    install: GameInstall,
    system: str,
    mod_roots: Sequence[Path] | None,
) -> tuple[EntityDetail, ...]:
    return _load_system_entity_index(install, system, mod_roots).details


def _invalidate_entity_caches_for_mutated_subtree(
    install: GameInstall | str | Path,
    *,
    phase: ContentPhase,
    relative_root: Path,
    mod_root: Path | None = None,
) -> tuple[str, ...]:
    invalidated_systems: list[str] = []
    for system in _entity_systems_for_mutated_subtree(phase, relative_root):
        if invalidate_system_entity_cache(install, system, mod_root=mod_root) > 0:
            invalidated_systems.append(system)
    return tuple(invalidated_systems)


def _load_system_entity_index(
    install: GameInstall,
    system: str,
    mod_roots: Sequence[Path] | None,
) -> _EntityQueryIndex:
    cache_key = _entity_query_cache_key(install, system, mod_roots)
    cached = _ENTITY_QUERY_CACHE.get(cache_key)
    if cached is not None:
        return cached

    details = _build_system_entity_details(install, system, mod_roots)
    index = _EntityQueryIndex(
        details=details,
        summaries=tuple(detail.summary for detail in details),
        by_name=_index_entity_details_by_name(details),
    )
    _ENTITY_QUERY_CACHE[cache_key] = index
    return index


def _entity_query_cache_key(
    install: GameInstall,
    system: str,
    mod_roots: Sequence[Path] | None,
) -> _EntityQueryCacheKey:
    return _EntityQueryCacheKey(
        install_root=install.root.resolve(),
        system=system,
        mod_roots=tuple(path.resolve() for path in mod_roots) if mod_roots is not None else (),
    )


def _invalidate_entity_query_cache(
    matcher: Callable[[_EntityQueryCacheKey], bool],
) -> int:
    matching_keys = [cache_key for cache_key in _ENTITY_QUERY_CACHE if matcher(cache_key)]
    for cache_key in matching_keys:
        _ENTITY_QUERY_CACHE.pop(cache_key, None)
    return len(matching_keys)


def _entity_systems_for_mutated_subtree(
    phase: ContentPhase,
    relative_root: Path,
) -> tuple[str, ...]:
    systems: list[str] = []
    for system, source_roots in _ENTITY_SYSTEM_SOURCE_ROOTS.items():
        if any(
            source_root.phase is phase
            and _relative_paths_overlap(relative_root, source_root.relative_root)
            for source_root in source_roots
        ):
            systems.append(system)
    return tuple(systems)


def _relative_paths_overlap(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _resolved_install_root(install: GameInstall | str | Path) -> Path:
    if isinstance(install, GameInstall):
        return install.root.resolve()
    return Path(install).resolve()


def _index_entity_details_by_name(details: Sequence[EntityDetail]) -> dict[str, EntityDetail]:
    by_name: dict[str, EntityDetail] = {}
    for detail in details:
        by_name.setdefault(detail.summary.name, detail)
    return by_name


def _build_system_entity_details(
    install: GameInstall,
    system: str,
    mod_roots: Sequence[Path] | None,
) -> tuple[EntityDetail, ...]:
    _entity_description_for(system)
    vfs = VirtualFilesystem.from_install(
        install,
        mod_roots=list(mod_roots) if mod_roots is not None else None,
    )

    if system == "economy":
        return _build_economy_entities(vfs)
    if system == "diplomacy":
        return _build_diplomacy_entities(vfs)
    if system == "government":
        return _build_government_entities(vfs)
    if system == "religion":
        return _build_religion_entities(vfs)
    if system == "map":
        return _build_map_entities(vfs)

    raise AssertionError(system)


def _build_economy_entities(vfs: VirtualFilesystem) -> tuple[EntityDetail, ...]:
    goods_documents = _load_documents(
        vfs,
        ContentPhase.IN_GAME,
        Path("common") / "goods",
        parse_goods_document,
    )
    price_documents = _load_documents(
        vfs,
        ContentPhase.IN_GAME,
        Path("common") / "prices",
        parse_price_document,
    )
    generic_action_documents = _load_documents(
        vfs,
        ContentPhase.IN_GAME,
        Path("common") / "generic_actions",
        parse_generic_action_document,
    )
    attribute_column_documents = _load_documents(
        vfs,
        ContentPhase.IN_GAME,
        Path("common") / "attribute_columns",
        parse_attribute_column_document,
    )
    catalog = build_market_catalog(
        goods_documents=goods_documents,
        price_documents=price_documents,
        generic_action_documents=generic_action_documents,
        attribute_column_documents=attribute_column_documents,
    )

    details: list[EntityDetail] = []
    for definition in sorted(catalog.goods_definitions, key=lambda item: item.name):
        summary = EntitySummary(
            system="economy",
            entity_kind="good",
            name=definition.name,
            group=definition.category,
            description=_join_summary_parts(
                f"method={definition.method}" if definition.method is not None else None,
                (
                    f"default_market_price={definition.default_market_price}"
                    if definition.default_market_price is not None
                    else None
                ),
            ),
        )
        details.append(
            EntityDetail(
                summary=summary,
                fields=_compact_fields(
                    ("method", definition.method),
                    ("category", definition.category),
                    ("default_market_price", definition.default_market_price),
                    ("base_production", definition.base_production),
                    ("food", definition.food),
                    ("transport_cost", definition.transport_cost),
                    ("is_slaves", definition.is_slaves),
                    ("inflation", definition.inflation),
                    ("custom_tags", definition.custom_tags),
                ),
                references=tuple(
                    [
                        EntityReference(
                            role="demand_add",
                            system="economy",
                            entity_kind="good",
                            target_name=amount.name,
                        )
                        for amount in definition.demand_add
                    ]
                    + [
                        EntityReference(
                            role="demand_multiply",
                            system="economy",
                            entity_kind="good",
                            target_name=amount.name,
                        )
                        for amount in definition.demand_multiply
                    ]
                    + [
                        EntityReference(
                            role="wealth_impact_threshold",
                            system="economy",
                            entity_kind="good",
                            target_name=amount.name,
                        )
                        for amount in definition.wealth_impact_threshold
                    ]
                ),
            )
        )

    return tuple(details)


def _build_diplomacy_entities(vfs: VirtualFilesystem) -> tuple[EntityDetail, ...]:
    catalog = build_diplomacy_graph_catalog(
        casus_belli_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "casus_belli",
            parse_casus_belli_document,
        ),
        wargoal_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "wargoals",
            parse_wargoal_document,
        ),
        peace_treaty_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "peace_treaties",
            parse_peace_treaty_document,
        ),
        subject_type_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "subject_types",
            parse_subject_type_document,
        ),
        country_interaction_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "country_interactions",
            parse_country_interaction_document,
        ),
    )

    details: list[EntityDetail] = []
    war_flow_catalog = catalog.war_flow_catalog
    wargoals_by_name = {
        definition.name: definition for definition in war_flow_catalog.wargoal_definitions
    }
    peace_treaties_by_casus_belli = _group_items_by_keys(
        war_flow_catalog.peace_treaty_definitions,
        lambda definition: collect_casus_belli_references(definition.body),
    )
    country_interactions_by_casus_belli = _group_items_by_keys(
        catalog.country_interaction_definitions,
        lambda definition: collect_casus_belli_references(definition.body),
    )
    for definition in sorted(war_flow_catalog.casus_belli_definitions, key=lambda item: item.name):
        linked_wargoal = (
            wargoals_by_name.get(definition.war_goal_type)
            if definition.war_goal_type is not None
            else None
        )
        peace_treaties = peace_treaties_by_casus_belli.get(definition.name, ())
        country_interactions = country_interactions_by_casus_belli.get(definition.name, ())
        summary = EntitySummary(
            system="diplomacy",
            entity_kind="casus_belli",
            name=definition.name,
            group=definition.war_goal_type,
            description=_join_summary_parts(
                f"speed={definition.speed}" if definition.speed is not None else None,
                "trade=yes" if definition.trade else None,
                "no_cb=yes" if definition.no_cb else None,
            ),
        )
        details.append(
            EntityDetail(
                summary=summary,
                fields=_compact_fields(
                    ("war_goal_type", definition.war_goal_type),
                    ("speed", definition.speed),
                    ("custom_tags", definition.custom_tags),
                    ("additional_war_enthusiasm", definition.additional_war_enthusiasm),
                    (
                        "additional_war_enthusiasm_attacker",
                        definition.additional_war_enthusiasm_attacker,
                    ),
                    (
                        "additional_war_enthusiasm_defender",
                        definition.additional_war_enthusiasm_defender,
                    ),
                    (
                        "antagonism_reduction_per_warworth_defender",
                        definition.antagonism_reduction_per_warworth_defender,
                    ),
                    ("max_warscore_from_battles", definition.max_warscore_from_battles),
                    ("allow_release_areas", definition.allow_release_areas),
                    ("allow_separate_peace", definition.allow_separate_peace),
                    ("allow_wars_on_own_subjects", definition.allow_wars_on_own_subjects),
                    ("allow_ports_for_reach_ai", definition.allow_ports_for_reach_ai),
                    ("can_expire", definition.can_expire),
                    ("cut_down_in_size_cb", definition.cut_down_in_size_cb),
                    ("no_cb", definition.no_cb),
                    ("trade", definition.trade),
                ),
                references=tuple(
                    (
                        [
                            EntityReference(
                                role="wargoal",
                                system="diplomacy",
                                entity_kind="wargoal",
                                target_name=linked_wargoal.name,
                            )
                        ]
                        if linked_wargoal is not None
                        else []
                    )
                    + [
                        EntityReference(
                            role="peace_treaty",
                            system="diplomacy",
                            entity_kind="peace_treaty",
                            target_name=peace_treaty.name,
                        )
                        for peace_treaty in peace_treaties
                    ]
                    + [
                        EntityReference(
                            role="country_interaction",
                            system="diplomacy",
                            entity_kind="country_interaction",
                            target_name=interaction.name,
                        )
                        for interaction in country_interactions
                    ]
                ),
            )
        )

    return tuple(details)


def _build_government_entities(vfs: VirtualFilesystem) -> tuple[EntityDetail, ...]:
    catalog = build_government_catalog(
        government_type_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "government_types",
            parse_government_type_document,
        ),
        government_reform_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "government_reforms",
            parse_government_reform_document,
        ),
        law_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "laws",
            parse_law_document,
        ),
        estate_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "estates",
            parse_estate_document,
        ),
        estate_privilege_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "estate_privileges",
            parse_estate_privilege_document,
        ),
        parliament_type_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "parliament_types",
            parse_parliament_type_document,
        ),
        parliament_agenda_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "parliament_agendas",
            parse_parliament_agenda_document,
        ),
        parliament_issue_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "parliament_issues",
            parse_parliament_issue_document,
        ),
    )

    details: list[EntityDetail] = []
    reforms_by_government = _group_items_by_keys(
        catalog.government_reform_definitions,
        lambda definition: (definition.government,) if definition.government is not None else (),
    )
    laws_by_government = _group_items_by_keys(
        catalog.law_definitions,
        lambda definition: definition.law_gov_groups,
    )
    for definition in sorted(catalog.government_type_definitions, key=lambda item: item.name):
        reforms = reforms_by_government.get(definition.name, ())
        laws = laws_by_government.get(definition.name, ())
        summary = EntitySummary(
            system="government",
            entity_kind="government_type",
            name=definition.name,
            group=definition.government_power,
            description=_join_summary_parts(
                (
                    f"default_estate={definition.default_character_estate}"
                    if definition.default_character_estate is not None
                    else None
                ),
                (
                    f"heir_selections={len(definition.heir_selections)}"
                    if definition.heir_selections
                    else None
                ),
            ),
        )
        details.append(
            EntityDetail(
                summary=summary,
                fields=_compact_fields(
                    ("government_power", definition.government_power),
                    ("heir_selections", definition.heir_selections),
                    ("default_character_estate", definition.default_character_estate),
                    ("use_regnal_number", definition.use_regnal_number),
                    ("generate_consorts", definition.generate_consorts),
                    (
                        "revolutionary_country_antagonism",
                        definition.revolutionary_country_antagonism,
                    ),
                ),
                references=tuple(
                    (
                        [
                            EntityReference(
                                role="default_estate",
                                system="government",
                                entity_kind="estate",
                                target_name=definition.default_character_estate,
                            )
                        ]
                        if definition.default_character_estate is not None
                        else []
                    )
                    + [
                        EntityReference(
                            role="reform",
                            system="government",
                            entity_kind="government_reform",
                            target_name=reform.name,
                        )
                        for reform in reforms
                    ]
                    + [
                        EntityReference(
                            role="law",
                            system="government",
                            entity_kind="law",
                            target_name=law.name,
                        )
                        for law in laws
                    ]
                ),
            )
        )

    return tuple(details)


def _build_religion_entities(vfs: VirtualFilesystem) -> tuple[EntityDetail, ...]:
    catalog = build_religion_catalog(
        religion_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "religions",
            parse_religion_document,
        ),
        religious_aspect_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "religious_aspects",
            parse_religious_aspect_document,
        ),
        religious_faction_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "religious_factions",
            parse_religious_faction_document,
        ),
        religious_focus_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "religious_focuses",
            parse_religious_focus_document,
        ),
        religious_school_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "religious_schools",
            parse_religious_school_document,
        ),
        religious_figure_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "religious_figures",
            parse_religious_figure_document,
        ),
        holy_site_documents=_load_documents(
            vfs,
            ContentPhase.IN_GAME,
            Path("common") / "holy_sites",
            parse_holy_site_document,
        ),
    )

    details: list[EntityDetail] = []
    aspect_definitions_by_religion = _group_items_by_keys(
        catalog.religious_aspect_definitions,
        lambda definition: definition.religions,
    )
    focus_definitions_by_name = {
        definition.name: definition for definition in catalog.religious_focus_definitions
    }
    faction_definitions_by_name = {
        definition.name: definition for definition in catalog.religious_faction_definitions
    }
    holy_site_definitions_by_religion = _group_items_by_keys(
        catalog.holy_site_definitions,
        lambda definition: definition.religions,
    )
    for definition in sorted(catalog.religion_definitions, key=lambda item: item.name):
        aspects = aspect_definitions_by_religion.get(definition.name, ())
        factions = tuple(
            resolved_faction
            for faction_name in definition.factions
            if (resolved_faction := faction_definitions_by_name.get(faction_name)) is not None
        )
        focuses = tuple(
            resolved_focus
            for focus_name in definition.religious_focuses
            if (resolved_focus := focus_definitions_by_name.get(focus_name)) is not None
        )
        schools = catalog.get_religious_schools_for_religion(definition.name)
        figures = catalog.get_religious_figures_for_religion(definition.name)
        holy_sites = holy_site_definitions_by_religion.get(definition.name, ())
        summary = EntitySummary(
            system="religion",
            entity_kind="religion",
            name=definition.name,
            group=definition.group,
            description=_join_summary_parts(
                f"focuses={len(focuses)}" if focuses else None,
                f"holy_sites={len(holy_sites)}" if holy_sites else None,
            ),
        )
        details.append(
            EntityDetail(
                summary=summary,
                fields=_compact_fields(
                    ("group", definition.group),
                    ("language", definition.language),
                    ("enable", definition.enable),
                    ("religious_focuses", definition.religious_focuses),
                    ("religious_schools", definition.religious_schools),
                    ("factions", definition.factions),
                    ("tags", definition.tags),
                    ("custom_tags", definition.custom_tags),
                ),
                references=tuple(
                    [
                        EntityReference(
                            role="religious_aspect",
                            system="religion",
                            entity_kind="religious_aspect",
                            target_name=aspect.name,
                        )
                        for aspect in aspects
                    ]
                    + [
                        EntityReference(
                            role="religious_faction",
                            system="religion",
                            entity_kind="religious_faction",
                            target_name=faction.name,
                        )
                        for faction in factions
                    ]
                    + [
                        EntityReference(
                            role="religious_focus",
                            system="religion",
                            entity_kind="religious_focus",
                            target_name=focus.name,
                        )
                        for focus in focuses
                    ]
                    + [
                        EntityReference(
                            role="religious_school",
                            system="religion",
                            entity_kind="religious_school",
                            target_name=school.name,
                        )
                        for school in schools
                    ]
                    + [
                        EntityReference(
                            role="religious_figure",
                            system="religion",
                            entity_kind="religious_figure",
                            target_name=figure.name,
                        )
                        for figure in figures
                    ]
                    + [
                        EntityReference(
                            role="holy_site",
                            system="religion",
                            entity_kind="holy_site",
                            target_name=site.name,
                        )
                        for site in holy_sites
                    ]
                ),
            )
        )

    return tuple(details)


def _build_map_entities(vfs: VirtualFilesystem) -> tuple[EntityDetail, ...]:
    hierarchy_document = _load_single_document(
        vfs,
        ContentPhase.IN_GAME,
        Path("map_data") / "definitions.txt",
        parse_location_hierarchy_document,
    )
    country_document = _load_single_document(
        vfs,
        ContentPhase.MAIN_MENU,
        Path("setup") / "start" / "10_countries.txt",
        parse_country_location_document,
    )
    setup_document = _load_single_document(
        vfs,
        ContentPhase.MAIN_MENU,
        Path("setup") / "start" / "21_locations.txt",
        parse_location_setup_document,
    )
    if hierarchy_document is None or country_document is None or setup_document is None:
        return ()

    linked_document = build_linked_location_document(
        hierarchy_document,
        country_document,
        setup_document,
    )
    details: list[EntityDetail] = []
    for definition in sorted(linked_document.definitions, key=lambda item: item.name):
        summary = EntitySummary(
            system="map",
            entity_kind="location",
            name=definition.name,
            group=definition.hierarchy.leaf_group if definition.hierarchy is not None else None,
            description=_join_summary_parts(
                (
                    f"capital_of={','.join(definition.capital_of)}"
                    if definition.capital_of
                    else None
                ),
                "setup=yes" if definition.has_location_setup else None,
            ),
        )
        details.append(
            EntityDetail(
                summary=summary,
                fields=_compact_fields(
                    (
                        "hierarchy_path",
                        (
                            definition.hierarchy.hierarchy_path
                            if definition.hierarchy is not None
                            else ()
                        ),
                    ),
                    ("capital_of", definition.capital_of),
                    (
                        "country_tags",
                        tuple(reference.country_tag for reference in definition.country_references),
                    ),
                    ("has_location_setup", definition.has_location_setup),
                ),
                references=tuple(
                    [
                        EntityReference(
                            role="country_reference",
                            system="map",
                            entity_kind="country",
                            target_name=reference.country_tag,
                        )
                        for reference in definition.country_references
                    ]
                    + [
                        EntityReference(
                            role="capital_of",
                            system="map",
                            entity_kind="country",
                            target_name=tag,
                        )
                        for tag in definition.capital_of
                    ]
                ),
            )
        )

    return tuple(details)


def _load_documents[DocumentT](
    vfs: VirtualFilesystem,
    phase: ContentPhase,
    relative_subpath: Path,
    parser: Callable[[str], DocumentT],
) -> tuple[DocumentT, ...]:
    return tuple(
        parser(_read_text(merged_file.winner.absolute_path))
        for merged_file in vfs.merge_phase(phase, relative_subpath)
        if merged_file.relative_path.suffix.lower() == ".txt"
    )


def _load_single_document[DocumentT](
    vfs: VirtualFilesystem,
    phase: ContentPhase,
    relative_path: Path,
    parser: Callable[[str], DocumentT],
) -> DocumentT | None:
    merged_file = vfs.get_merged_file(phase, relative_path)
    if merged_file is None:
        return None
    return parser(_read_text(merged_file.winner.absolute_path))


def _group_items_by_keys[ItemT](
    items: Sequence[ItemT],
    key_selector: Callable[[ItemT], Sequence[str]],
) -> dict[str, tuple[ItemT, ...]]:
    grouped: dict[str, list[ItemT]] = {}
    for item in items:
        for key in key_selector(item):
            grouped.setdefault(key, []).append(item)
    return {key: tuple(values) for key, values in grouped.items()}


def _compact_fields(
    *pairs: tuple[str, BrowseValue | None],
) -> tuple[EntityField, ...]:
    fields: list[EntityField] = []
    for name, value in pairs:
        if value is None:
            continue
        if isinstance(value, tuple) and not value:
            continue
        fields.append(EntityField(name=name, value=value))
    return tuple(fields)


def _join_summary_parts(*parts: str | None) -> str | None:
    filtered = tuple(part for part in parts if part)
    if not filtered:
        return None
    return "; ".join(filtered)


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


__all__ = [
    "EntityDetail",
    "EntityField",
    "EntityReference",
    "EntitySummary",
    "EntitySystemInfo",
    "InstallPhaseRoot",
    "InstallSourceSummary",
    "InstallSummary",
    "SystemInfo",
    "SystemReport",
    "format_install_summary",
    "format_system_report",
    "get_system_entity",
    "get_system_report",
    "invalidate_system_entity_cache",
    "inspect_install",
    "list_entity_systems",
    "list_system_entities",
    "list_supported_systems",
    "summarize_install",
]