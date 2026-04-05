"""Structured read-only browser model over the stable core inspection facade."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import eu5miner.inspection as inspection
from eu5miner import GameInstall


@dataclass(frozen=True)
class BrowserSection:
    title: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class BrowserPage:
    key: str
    title: str
    description: str
    status: str
    sections: tuple[BrowserSection, ...]


@dataclass(frozen=True)
class BrowserModel:
    supported_systems: tuple[inspection.SystemInfo, ...]
    entity_systems: tuple[inspection.EntitySystemInfo, ...]
    pages: tuple[BrowserPage, ...]
    selected_page_key: str

    def page_keys(self) -> tuple[str, ...]:
        return tuple(page.key for page in self.pages)


def build_browser_model(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    selected_entity_system: str | None = None,
    selected_entity_name: str | None = None,
    include_all_systems: bool = False,
    language: str = "english",
) -> BrowserModel:
    supported_systems = inspection.list_supported_systems()
    entity_systems = inspection.list_entity_systems()
    _validate_selected_system(supported_systems, selected_system)
    _validate_selected_entity_system(entity_systems, selected_entity_system)
    _validate_selected_entity_name(selected_entity_system, selected_entity_name)

    summary: inspection.InstallSummary | None = None
    report_pages: list[BrowserPage] = []
    entity_list_pages: list[BrowserPage] = []
    entity_detail_pages: list[BrowserPage] = []
    ready_report_names: tuple[str, ...] = ()
    unavailable_report_names: tuple[str, ...] = ()
    ready_entity_list_names: tuple[str, ...] = ()
    unavailable_entity_list_names: tuple[str, ...] = ()
    ready_entity_detail_names: tuple[str, ...] = ()
    unavailable_entity_detail_names: tuple[str, ...] = ()

    systems_to_load = _resolve_systems_to_load(
        supported_systems,
        selected_system=selected_system,
        include_all_systems=include_all_systems,
    )
    entity_systems_to_load = _resolve_entity_systems_to_load(
        entity_systems,
        selected_entity_system=selected_entity_system,
        include_all_systems=include_all_systems,
    )

    if install_root is not None:
        summary = inspection.inspect_install(install_root)
        install = GameInstall.discover(summary.root)

        if systems_to_load:
            report_pages = [
                _build_report_page(install, info, language=language)
                for info in supported_systems
                if info.name in systems_to_load
            ]
            ready_report_names = tuple(page.key for page in report_pages if page.status == "ready")
            unavailable_report_names = tuple(
                page.key for page in report_pages if page.status != "ready"
            )

        if entity_systems_to_load:
            entity_list_pages = [
                _build_entity_list_page(install, info)
                for info in entity_systems
                if info.name in entity_systems_to_load
            ]
            ready_entity_list_names = tuple(
                page.key for page in entity_list_pages if page.status == "ready"
            )
            unavailable_entity_list_names = tuple(
                page.key for page in entity_list_pages if page.status != "ready"
            )

        if selected_entity_system is not None and selected_entity_name is not None:
            entity_info = _entity_system_info(entity_systems, selected_entity_system)
            detail_page = _build_entity_detail_page(
                install,
                entity_info,
                selected_entity_name,
            )
            entity_detail_pages = [detail_page]
            if detail_page.status == "ready":
                ready_entity_detail_names = (detail_page.key,)
            else:
                unavailable_entity_detail_names = (detail_page.key,)

    overview_page = _build_overview_page(
        supported_systems,
        entity_systems,
        summary,
        selected_system=selected_system,
        selected_entity_system=selected_entity_system,
        selected_entity_name=selected_entity_name,
        include_all_systems=include_all_systems,
        ready_report_names=ready_report_names,
        unavailable_report_names=unavailable_report_names,
        ready_entity_list_names=ready_entity_list_names,
        unavailable_entity_list_names=unavailable_entity_list_names,
        ready_entity_detail_names=ready_entity_detail_names,
        unavailable_entity_detail_names=unavailable_entity_detail_names,
    )
    pages = (
        overview_page,
        *report_pages,
        *entity_list_pages,
        *entity_detail_pages,
    )
    selected_page_key = _resolve_selected_page_key(
        pages,
        selected_system=selected_system,
        selected_entity_system=selected_entity_system,
        selected_entity_name=selected_entity_name,
    )
    return BrowserModel(
        supported_systems=supported_systems,
        entity_systems=entity_systems,
        pages=pages,
        selected_page_key=selected_page_key,
    )


def render_browser_model(model: BrowserModel) -> str:
    lines = [
        "EU5MinerGUI read-only browser ready.",
        "Stable inspection facade available.",
        f"Selected page: {model.selected_page_key}",
        "Available pages:",
        *(
            f"- {page.key}: {page.title}{_format_page_status_suffix(page)}"
            for page in model.pages
        ),
    ]

    for page in model.pages:
        lines.extend(("", f"== {page.title} ==", page.description))
        for section in page.sections:
            lines.append(f"{section.title}:")
            lines.extend(f"- {line}" for line in section.lines)

    return "\n".join(lines)


def _validate_selected_system(
    supported_systems: tuple[inspection.SystemInfo, ...],
    selected_system: str | None,
) -> None:
    if selected_system is None:
        return

    valid_system_names = {info.name for info in supported_systems}
    if selected_system not in valid_system_names:
        valid_systems = ", ".join(sorted(valid_system_names))
        raise KeyError(f"Unknown system '{selected_system}'. Valid systems: {valid_systems}")


def _validate_selected_entity_system(
    entity_systems: tuple[inspection.EntitySystemInfo, ...],
    selected_entity_system: str | None,
) -> None:
    if selected_entity_system is None:
        return

    valid_system_names = {info.name for info in entity_systems}
    if selected_entity_system not in valid_system_names:
        valid_systems = ", ".join(sorted(valid_system_names))
        raise KeyError(
            "Unknown entity system "
            f"'{selected_entity_system}'. Valid systems: {valid_systems}"
        )


def _validate_selected_entity_name(
    selected_entity_system: str | None,
    selected_entity_name: str | None,
) -> None:
    if selected_entity_name is None:
        return
    if selected_entity_system is None:
        raise ValueError("An entity name requires a selected entity system.")


def _resolve_systems_to_load(
    supported_systems: tuple[inspection.SystemInfo, ...],
    *,
    selected_system: str | None,
    include_all_systems: bool,
) -> tuple[str, ...]:
    if include_all_systems:
        return tuple(info.name for info in supported_systems)
    if selected_system is not None:
        return (selected_system,)
    return ()


def _resolve_entity_systems_to_load(
    entity_systems: tuple[inspection.EntitySystemInfo, ...],
    *,
    selected_entity_system: str | None,
    include_all_systems: bool,
) -> tuple[str, ...]:
    if include_all_systems:
        return tuple(info.name for info in entity_systems)
    if selected_entity_system is not None:
        return (selected_entity_system,)
    return ()


def _build_overview_page(
    supported_systems: tuple[inspection.SystemInfo, ...],
    entity_systems: tuple[inspection.EntitySystemInfo, ...],
    summary: inspection.InstallSummary | None,
    *,
    selected_system: str | None,
    selected_entity_system: str | None,
    selected_entity_name: str | None,
    include_all_systems: bool,
    ready_report_names: tuple[str, ...],
    unavailable_report_names: tuple[str, ...],
    ready_entity_list_names: tuple[str, ...],
    unavailable_entity_list_names: tuple[str, ...],
    ready_entity_detail_names: tuple[str, ...],
    unavailable_entity_detail_names: tuple[str, ...],
) -> BrowserPage:
    requested_report_scope = (
        "all supported reports"
        if include_all_systems
        else selected_system or "overview only"
    )
    requested_entity_scope = (
        "all covered entity lists"
        if include_all_systems
        else selected_entity_system or "none"
    )
    sections = [
        BrowserSection(
            title="Browser status",
            lines=(
                f"Requested report scope: {requested_report_scope}",
                f"Requested entity scope: {requested_entity_scope}",
                f"Requested entity detail: {selected_entity_name or 'none'}",
                f"Install summary loaded: {'yes' if summary is not None else 'no'}",
                (
                    "Ready report pages: "
                    f"{', '.join(ready_report_names) if ready_report_names else 'none'}"
                ),
                (
                    "Unavailable report pages: "
                    f"{', '.join(unavailable_report_names) if unavailable_report_names else 'none'}"
                ),
                (
                    "Ready entity list pages: "
                    f"{', '.join(ready_entity_list_names) if ready_entity_list_names else 'none'}"
                ),
                (
                    "Unavailable entity list pages: "
                    f"{_format_page_name_list(unavailable_entity_list_names)}"
                ),
                (
                    "Ready entity detail pages: "
                    f"{_format_page_name_list(ready_entity_detail_names)}"
                ),
                (
                    "Unavailable entity detail pages: "
                    f"{_format_page_name_list(unavailable_entity_detail_names)}"
                ),
            ),
        ),
        BrowserSection(
            title="Supported systems",
            lines=tuple(f"{info.name}: {info.description}" for info in supported_systems),
        ),
        BrowserSection(
            title="Browsable entity systems",
            lines=tuple(
                f"{info.name}: {info.primary_entity_kind} - {info.description}"
                for info in entity_systems
            ),
        ),
    ]

    if summary is None:
        unavailable_lines = ["Not loaded."]
        if selected_system is not None or include_all_systems:
            unavailable_lines.append("System reports require an install root.")
        if (
            selected_entity_system is not None
            or selected_entity_name is not None
            or include_all_systems
        ):
            unavailable_lines.append("Entity list and detail pages require an install root.")
        sections.append(
            BrowserSection(
                title="Install summary",
                lines=tuple(unavailable_lines),
            )
        )
    else:
        sections.extend(
            (
                BrowserSection(
                    title="Install roots",
                    lines=(
                        f"Install root: {summary.root}",
                        f"Game dir: {summary.game_dir}",
                        f"DLC dir: {summary.dlc_dir}",
                        f"Mod dir: {summary.mod_dir}",
                    ),
                ),
                BrowserSection(
                    title="Phase roots",
                    lines=tuple(
                        f"{phase_root.phase.value}: {phase_root.path}"
                        for phase_root in summary.phase_roots
                    ),
                ),
                BrowserSection(
                    title="Content sources",
                    lines=tuple(_format_source_summary(source) for source in summary.sources),
                ),
            )
        )

    return BrowserPage(
        key="overview",
        title="Install overview",
        description=(
            "Browse one install summary, stable system reports, and covered entity list/detail "
            "pages from eu5miner.inspection."
        ),
        status="ready",
        sections=tuple(sections),
    )


def _build_report_page(
    install: GameInstall,
    info: inspection.SystemInfo,
    *,
    language: str,
) -> BrowserPage:
    try:
        report = inspection.get_system_report(install, info.name, language=language)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return _build_unavailable_system_page(info, str(exc))

    return BrowserPage(
        key=_report_page_key(report.name),
        title=f"{report.name} system report",
        description=info.description,
        status="ready",
        sections=(
            BrowserSection(
                title="Representative files",
                lines=report.representative_keys,
            ),
            BrowserSection(
                title="Summary",
                lines=report.summary_lines,
            ),
        ),
    )


def _build_entity_list_page(
    install: GameInstall,
    info: inspection.EntitySystemInfo,
) -> BrowserPage:
    try:
        entities = inspection.list_system_entities(install, info.name)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return _build_unavailable_entity_list_page(info, str(exc))

    if not entities:
        return _build_unavailable_entity_list_page(
            info,
            "No browseable entities available from selected install.",
        )

    return BrowserPage(
        key=_entity_list_page_key(info.name),
        title=f"{info.name} entities",
        description=info.description,
        status="ready",
        sections=(
            BrowserSection(
                title="Browse status",
                lines=(
                    f"Primary entity kind: {info.primary_entity_kind}",
                    f"Entity count: {len(entities)}",
                ),
            ),
            BrowserSection(
                title="Entities",
                lines=tuple(_format_entity_summary(entity) for entity in entities),
            ),
        ),
    )


def _build_entity_detail_page(
    install: GameInstall,
    info: inspection.EntitySystemInfo,
    entity_name: str,
) -> BrowserPage:
    try:
        detail = inspection.get_system_entity(install, info.name, entity_name)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return _build_unavailable_entity_detail_page(info, entity_name, str(exc))

    return BrowserPage(
        key=_entity_detail_page_key(info.name, detail.summary.name),
        title=f"{detail.summary.name} {detail.summary.entity_kind}",
        description=info.description,
        status="ready",
        sections=(
            BrowserSection(
                title="Summary",
                lines=(
                    f"System: {detail.summary.system}",
                    f"Entity kind: {detail.summary.entity_kind}",
                    f"Name: {detail.summary.name}",
                    f"Group: {detail.summary.group or 'none'}",
                    f"Description: {detail.summary.description or 'none'}",
                ),
            ),
            BrowserSection(
                title="Fields",
                lines=tuple(
                    f"{field.name}: {_format_browse_value(field.value)}"
                    for field in detail.fields
                )
                or ("No fields.",),
            ),
            BrowserSection(
                title="References",
                lines=tuple(_format_entity_reference(reference) for reference in detail.references)
                or ("No references.",),
            ),
        ),
    )


def _build_unavailable_system_page(info: inspection.SystemInfo, reason: str) -> BrowserPage:
    return BrowserPage(
        key=_report_page_key(info.name),
        title=f"{info.name} system report",
        description=info.description,
        status="unavailable",
        sections=(
            BrowserSection(
                title="Status",
                lines=(
                    "Unavailable from selected install.",
                    f"Reason: {reason}",
                ),
            ),
        ),
    )


def _build_unavailable_entity_list_page(
    info: inspection.EntitySystemInfo,
    reason: str,
) -> BrowserPage:
    return BrowserPage(
        key=_entity_list_page_key(info.name),
        title=f"{info.name} entities",
        description=info.description,
        status="unavailable",
        sections=(
            BrowserSection(
                title="Status",
                lines=(
                    "Unavailable from selected install.",
                    f"Reason: {reason}",
                ),
            ),
        ),
    )


def _build_unavailable_entity_detail_page(
    info: inspection.EntitySystemInfo,
    entity_name: str,
    reason: str,
) -> BrowserPage:
    return BrowserPage(
        key=_entity_detail_page_key(info.name, entity_name),
        title=f"{entity_name} {info.primary_entity_kind}",
        description=info.description,
        status="unavailable",
        sections=(
            BrowserSection(
                title="Status",
                lines=(
                    "Unavailable from selected install.",
                    f"Reason: {reason}",
                ),
            ),
        ),
    )


def _entity_system_info(
    entity_systems: tuple[inspection.EntitySystemInfo, ...],
    selected_entity_system: str,
) -> inspection.EntitySystemInfo:
    for info in entity_systems:
        if info.name == selected_entity_system:
            return info
    raise AssertionError(selected_entity_system)


def _report_page_key(system: str) -> str:
    return f"report:{system}"


def _entity_list_page_key(system: str) -> str:
    return f"entities:{system}"


def _entity_detail_page_key(system: str, entity_name: str) -> str:
    return f"entity:{system}:{entity_name}"


def _format_entity_summary(summary: inspection.EntitySummary) -> str:
    line = summary.name
    if summary.group is not None:
        line = f"{line} [{summary.group}]"
    if summary.description is not None:
        line = f"{line}: {summary.description}"
    return line


def _format_entity_reference(reference: inspection.EntityReference) -> str:
    return (
        f"{reference.role} -> {reference.system}/{reference.entity_kind}: "
        f"{reference.target_name}"
    )


def _format_browse_value(value: inspection.BrowseValue) -> str:
    if isinstance(value, tuple):
        return ", ".join(value) if value else "(none)"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def _format_source_summary(source: inspection.InstallSourceSummary) -> str:
    replace_paths = (
        f" replace_paths={', '.join(source.replace_paths)}" if source.replace_paths else ""
    )
    return (
        f"{source.kind.value}:{source.name} priority={source.priority} root={source.root}"
        f"{replace_paths}"
    )


def _format_page_name_list(page_names: tuple[str, ...]) -> str:
    return ", ".join(page_names) if page_names else "none"


def _resolve_selected_page_key(
    pages: tuple[BrowserPage, ...],
    *,
    selected_system: str | None,
    selected_entity_system: str | None,
    selected_entity_name: str | None,
) -> str:
    page_keys = {page.key for page in pages}

    if selected_entity_system is not None and selected_entity_name is not None:
        detail_key = _entity_detail_page_key(selected_entity_system, selected_entity_name)
        if detail_key in page_keys:
            return detail_key

    if selected_entity_system is not None:
        list_key = _entity_list_page_key(selected_entity_system)
        if list_key in page_keys:
            return list_key

    if selected_system is not None:
        report_key = _report_page_key(selected_system)
        if report_key in page_keys:
            return report_key

    return "overview"


def _format_page_status_suffix(page: BrowserPage) -> str:
    if page.status == "ready":
        return ""
    return f" ({page.status})"
