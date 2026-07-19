"""Thin religion helper views over stable core grouped-package seams."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from eu5miner import GameInstall
from eu5miner.domains.religion import (
    ReligionReferenceEdge,
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


@dataclass(frozen=True)
class ReligionHelperInfo:
    name: str
    title: str
    description: str
    representative_keys: tuple[str, ...]


@dataclass(frozen=True)
class ReligionHelperSection:
    title: str
    lines: tuple[str, ...]
    use_section_line_limit: bool = True


@dataclass(frozen=True)
class ReligionHelperView:
    info: ReligionHelperInfo
    sections: tuple[ReligionHelperSection, ...]
    navigation_hints: tuple[str, ...] = ()


_RELIGION_OVERVIEW_KEYS: Final[tuple[str, ...]] = (
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

_RELIGION_HELPERS: Final[tuple[ReligionHelperInfo, ...]] = (
    ReligionHelperInfo(
        name="religion-overview",
        title="religion-overview helper report",
        description=(
            "Representative religion coverage built from "
            "eu5miner.domains.religion over install sample files."
        ),
        representative_keys=_RELIGION_OVERVIEW_KEYS,
    ),
)


def list_religion_helpers() -> tuple[ReligionHelperInfo, ...]:
    return _RELIGION_HELPERS


def get_religion_helper_info(name: str) -> ReligionHelperInfo | None:
    for info in _RELIGION_HELPERS:
        if info.name == name:
            return info
    return None


def build_religion_helper_view(
    install: GameInstall,
    helper_name: str,
) -> ReligionHelperView:
    info = get_religion_helper_info(helper_name)
    if info is None:
        valid_names = ", ".join(helper.name for helper in _RELIGION_HELPERS)
        raise KeyError(
            f"Unknown religion helper '{helper_name}'. Valid helpers: {valid_names}"
        )

    representative_files = install.representative_files()
    _require_representative_files(representative_files, info.representative_keys)
    return _build_religion_overview_view(info, representative_files)


def _build_religion_overview_view(
    info: ReligionHelperInfo,
    representative_files: dict[str, Path],
) -> ReligionHelperView:
    religion_documents = tuple(
        parse_religion_document(_read_text(representative_files[key]))
        for key in (
            "religion_sample",
            "religion_secondary_sample",
            "religion_muslim_sample",
            "religion_tonal_sample",
            "religion_dharmic_sample",
        )
    )
    religious_aspect_documents = tuple(
        parse_religious_aspect_document(_read_text(representative_files[key]))
        for key in (
            "religious_aspect_sample",
            "religious_aspect_secondary_sample",
        )
    )
    religious_faction_documents = (
        parse_religious_faction_document(
            _read_text(representative_files["religious_faction_sample"])
        ),
    )
    religious_focus_documents = (
        parse_religious_focus_document(
            _read_text(representative_files["religious_focus_sample"])
        ),
    )
    religious_school_documents = tuple(
        parse_religious_school_document(_read_text(representative_files[key]))
        for key in (
            "religious_school_sample",
            "religious_school_secondary_sample",
        )
    )
    religious_figure_documents = tuple(
        parse_religious_figure_document(_read_text(representative_files[key]))
        for key in (
            "religious_figure_sample",
            "religious_figure_secondary_sample",
        )
    )
    holy_site_type_documents = (
        parse_holy_site_type_document(_read_text(representative_files["holy_site_type_sample"])),
    )
    holy_site_documents = tuple(
        parse_holy_site_document(_read_text(representative_files[key]))
        for key in ("holy_site_sample", "holy_site_secondary_sample")
    )
    catalog = build_religion_catalog(
        religion_documents=religion_documents,
        religious_aspect_documents=religious_aspect_documents,
        religious_faction_documents=religious_faction_documents,
        religious_focus_documents=religious_focus_documents,
        religious_school_documents=religious_school_documents,
        religious_figure_documents=religious_figure_documents,
        holy_site_documents=holy_site_documents,
    )
    report = build_religion_report(catalog)

    return ReligionHelperView(
        info=info,
        sections=(
            ReligionHelperSection(
                title="Representative files",
                lines=info.representative_keys,
            ),
            ReligionHelperSection(
                title="Coverage summary",
                lines=(
                    f"Religion definitions: {len(catalog.religion_definitions)}",
                    (
                        "Religious aspect definitions: "
                        f"{len(catalog.religious_aspect_definitions)}"
                    ),
                    (
                        "Religious faction definitions: "
                        f"{len(catalog.religious_faction_definitions)}"
                    ),
                    (
                        "Religious focus definitions: "
                        f"{len(catalog.religious_focus_definitions)}"
                    ),
                    (
                        "Religious school definitions: "
                        f"{len(catalog.religious_school_definitions)}"
                    ),
                    (
                        "Religious figure definitions: "
                        f"{len(catalog.religious_figure_definitions)}"
                    ),
                    (
                        "Holy site type definitions: "
                        f"{sum(len(document.definitions) for document in holy_site_type_documents)}"
                    ),
                    f"Holy site definitions: {len(catalog.holy_site_definitions)}",
                    (
                        "Religion -> aspect links: "
                        f"{len(report.religion_aspect_links)}"
                    ),
                    (
                        "Religion -> faction links: "
                        f"{len(report.religion_faction_links)}"
                    ),
                    (
                        "Religion -> focus links: "
                        f"{len(report.religion_focus_links)}"
                    ),
                    (
                        "Religion -> school links: "
                        f"{len(report.religion_school_links)}"
                    ),
                    (
                        "Religion -> holy site links: "
                        f"{len(report.religion_holy_site_links)}"
                    ),
                    (
                        "Religion -> figure links: "
                        f"{len(report.religion_figure_links)}"
                    ),
                ),
            ),
            ReligionHelperSection(
                title="Missing references",
                lines=(
                    "Missing religious faction references: "
                    f"{_format_name_list(report.missing_religious_faction_references)}",
                    "Missing religious focus references: "
                    f"{_format_name_list(report.missing_religious_focus_references)}",
                    "Missing religious school references: "
                    f"{_format_name_list(report.missing_religious_school_references)}",
                ),
            ),
            ReligionHelperSection(
                title="Representative links",
                lines=(
                    *_format_edge_lines(
                        label="Religion -> aspect",
                        edges=report.religion_aspect_links,
                    ),
                    *_format_edge_lines(
                        label="Religion -> faction",
                        edges=report.religion_faction_links,
                    ),
                    *_format_edge_lines(
                        label="Religion -> focus",
                        edges=report.religion_focus_links,
                    ),
                    *_format_edge_lines(
                        label="Religion -> school",
                        edges=report.religion_school_links,
                    ),
                    *_format_edge_lines(
                        label="Religion -> holy site",
                        edges=report.religion_holy_site_links,
                    ),
                    *_format_edge_lines(
                        label="Religion -> figure",
                        edges=report.religion_figure_links,
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
        "Representative religion helper files missing from selected install: "
        + ", ".join(missing_keys)
    )


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _format_name_list(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _format_edge_lines(
    *,
    label: str,
    edges: tuple[ReligionReferenceEdge, ...],
) -> tuple[str, ...]:
    lines: list[str] = []
    for edge in edges:
        for referenced_name in edge.referenced_names:
            lines.append(f"{label}: {edge.source_name} -> {referenced_name}")
    return tuple(lines)