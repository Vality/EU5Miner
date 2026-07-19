"""Thin diplomacy helper views over stable core grouped-package seams."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from eu5miner import GameInstall
from eu5miner.domains.diplomacy import (
    DiplomacyReferenceEdge,
    WarReferenceEdge,
    build_diplomacy_graph_catalog,
    build_diplomacy_graph_report,
    build_war_flow_catalog,
    build_war_flow_report,
    parse_casus_belli_document,
    parse_character_interaction_document,
    parse_country_interaction_document,
    parse_peace_treaty_document,
    parse_subject_type_document,
    parse_wargoal_document,
)


@dataclass(frozen=True)
class DiplomacyHelperInfo:
    name: str
    title: str
    description: str
    representative_keys: tuple[str, ...]


@dataclass(frozen=True)
class DiplomacyHelperSection:
    title: str
    lines: tuple[str, ...]
    use_section_line_limit: bool = True


@dataclass(frozen=True)
class DiplomacyHelperView:
    info: DiplomacyHelperInfo
    sections: tuple[DiplomacyHelperSection, ...]
    navigation_hints: tuple[str, ...] = ()


_WAR_FLOW_KEYS: Final[tuple[str, ...]] = (
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
)

_DIPLOMACY_GRAPH_KEYS: Final[tuple[str, ...]] = (
    *_WAR_FLOW_KEYS,
    "country_interaction_sample",
    "country_interaction_secondary_sample",
    "character_interaction_sample",
    "character_interaction_secondary_sample",
    "character_interaction_ui_sample",
)

_DIPLOMACY_HELPERS: Final[tuple[DiplomacyHelperInfo, ...]] = (
    DiplomacyHelperInfo(
        name="war-flow",
        title="war-flow helper report",
        description=(
            "Representative war-flow coverage built from "
            "eu5miner.domains.diplomacy over install sample files."
        ),
        representative_keys=_WAR_FLOW_KEYS,
    ),
    DiplomacyHelperInfo(
        name="diplomacy-graph",
        title="diplomacy-graph helper report",
        description=(
            "Representative diplomacy-graph coverage built from "
            "eu5miner.domains.diplomacy over install sample files."
        ),
        representative_keys=_DIPLOMACY_GRAPH_KEYS,
    ),
)


def list_diplomacy_helpers() -> tuple[DiplomacyHelperInfo, ...]:
    return _DIPLOMACY_HELPERS


def get_diplomacy_helper_info(name: str) -> DiplomacyHelperInfo | None:
    for info in _DIPLOMACY_HELPERS:
        if info.name == name:
            return info
    return None


def build_diplomacy_helper_view(
    install: GameInstall,
    helper_name: str,
) -> DiplomacyHelperView:
    info = get_diplomacy_helper_info(helper_name)
    if info is None:
        valid_names = ", ".join(helper.name for helper in _DIPLOMACY_HELPERS)
        raise KeyError(
            f"Unknown diplomacy helper '{helper_name}'. Valid helpers: {valid_names}"
        )

    representative_files = install.representative_files()
    _require_representative_files(representative_files, info.representative_keys)
    if helper_name == "war-flow":
        return _build_war_flow_view(info, representative_files)
    return _build_diplomacy_graph_view(info, representative_files)


def _build_war_flow_view(
    info: DiplomacyHelperInfo,
    representative_files: dict[str, Path],
) -> DiplomacyHelperView:
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
    catalog = build_war_flow_catalog(
        casus_belli_documents=casus_belli_documents,
        wargoal_documents=wargoal_documents,
        peace_treaty_documents=peace_treaty_documents,
        subject_type_documents=subject_type_documents,
    )
    report = build_war_flow_report(catalog)

    return DiplomacyHelperView(
        info=info,
        sections=(
            DiplomacyHelperSection(
                title="Representative files",
                lines=info.representative_keys,
            ),
            DiplomacyHelperSection(
                title="Coverage summary",
                lines=(
                    f"Casus belli definitions: {len(catalog.casus_belli_definitions)}",
                    f"Wargoal definitions: {len(catalog.wargoal_definitions)}",
                    f"Peace treaty definitions: {len(catalog.peace_treaty_definitions)}",
                    f"Subject type definitions: {len(catalog.subject_type_definitions)}",
                    f"Casus belli -> wargoal links: {len(report.casus_belli_wargoal_links)}",
                    "Peace treaty -> casus belli links: "
                    f"{len(report.peace_treaty_casus_belli_links)}",
                    "Peace treaty -> subject type links: "
                    f"{len(report.peace_treaty_subject_type_links)}",
                ),
            ),
            DiplomacyHelperSection(
                title="Missing references",
                lines=(
                    "Missing wargoal references: "
                    f"{_format_name_list(report.missing_wargoal_references)}",
                    "Missing casus belli references: "
                    f"{_format_name_list(report.missing_casus_belli_references)}",
                    "Missing subject type references: "
                    f"{_format_name_list(report.missing_subject_type_references)}",
                ),
            ),
            DiplomacyHelperSection(
                title="Representative links",
                lines=(
                    *_format_edge_lines(
                        label="Casus belli -> wargoal",
                        edges=report.casus_belli_wargoal_links,
                    ),
                    *_format_edge_lines(
                        label="Peace treaty -> casus belli",
                        edges=report.peace_treaty_casus_belli_links,
                    ),
                    *_format_edge_lines(
                        label="Peace treaty -> subject type",
                        edges=report.peace_treaty_subject_type_links,
                    ),
                )
                or ("No representative links.",),
            ),
        ),
    )


def _build_diplomacy_graph_view(
    info: DiplomacyHelperInfo,
    representative_files: dict[str, Path],
) -> DiplomacyHelperView:
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
        for key in (
            "country_interaction_sample",
            "country_interaction_secondary_sample",
        )
    )
    character_interaction_documents = tuple(
        parse_character_interaction_document(_read_text(representative_files[key]))
        for key in (
            "character_interaction_sample",
            "character_interaction_secondary_sample",
            "character_interaction_ui_sample",
        )
    )
    catalog = build_diplomacy_graph_catalog(
        casus_belli_documents=casus_belli_documents,
        wargoal_documents=wargoal_documents,
        peace_treaty_documents=peace_treaty_documents,
        subject_type_documents=subject_type_documents,
        country_interaction_documents=country_interaction_documents,
        character_interaction_documents=character_interaction_documents,
    )
    report = build_diplomacy_graph_report(catalog)

    return DiplomacyHelperView(
        info=info,
        sections=(
            DiplomacyHelperSection(
                title="Representative files",
                lines=info.representative_keys,
            ),
            DiplomacyHelperSection(
                title="Coverage summary",
                lines=(
                    "Country interaction definitions: "
                    f"{len(catalog.country_interaction_definitions)}",
                    "Character interaction definitions: "
                    f"{len(catalog.character_interaction_definitions)}",
                    "Peace treaty -> casus belli links: "
                    f"{len(report.peace_treaty_casus_belli_links)}",
                    "Peace treaty -> subject type links: "
                    f"{len(report.peace_treaty_subject_type_links)}",
                    "Country interaction -> casus belli links: "
                    f"{len(report.country_interaction_casus_belli_links)}",
                    "Country interaction -> subject type links: "
                    f"{len(report.country_interaction_subject_type_links)}",
                    "Country interaction -> country interaction links: "
                    f"{len(report.country_interaction_links)}",
                    "Character interaction -> subject type links: "
                    f"{len(report.character_interaction_subject_type_links)}",
                ),
            ),
            DiplomacyHelperSection(
                title="Missing references",
                lines=(
                    "Missing casus belli references: "
                    f"{_format_name_list(report.missing_casus_belli_references)}",
                    "Missing subject type references: "
                    f"{_format_name_list(report.missing_subject_type_references)}",
                    "Missing country interaction references: "
                    f"{_format_name_list(report.missing_country_interaction_references)}",
                ),
            ),
            DiplomacyHelperSection(
                title="Representative links",
                lines=(
                    *_format_edge_lines(
                        label="Peace treaty -> casus belli",
                        edges=report.peace_treaty_casus_belli_links,
                    ),
                    *_format_edge_lines(
                        label="Peace treaty -> subject type",
                        edges=report.peace_treaty_subject_type_links,
                    ),
                    *_format_edge_lines(
                        label="Country interaction -> casus belli",
                        edges=report.country_interaction_casus_belli_links,
                    ),
                    *_format_edge_lines(
                        label="Country interaction -> subject type",
                        edges=report.country_interaction_subject_type_links,
                    ),
                    *_format_edge_lines(
                        label="Country interaction -> country interaction",
                        edges=report.country_interaction_links,
                    ),
                    *_format_edge_lines(
                        label="Character interaction -> subject type",
                        edges=report.character_interaction_subject_type_links,
                    ),
                )
                or ("No representative links.",),
            ),
        ),
    )


def _require_representative_files(
    representative_files: dict[str, Path],
    representative_keys: tuple[str, ...],
) -> None:
    missing_keys = [key for key in representative_keys if not representative_files[key].exists()]
    if not missing_keys:
        return
    raise FileNotFoundError(
        "Representative diplomacy helper files missing from selected install: "
        + ", ".join(missing_keys)
    )


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _format_name_list(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _format_edge_lines(
    *,
    label: str,
    edges: tuple[WarReferenceEdge | DiplomacyReferenceEdge, ...],
) -> tuple[str, ...]:
    lines: list[str] = []
    for edge in edges:
        for referenced_name in edge.referenced_names:
            lines.append(f"{label}: {edge.source_name} -> {referenced_name}")
    return tuple(lines)
