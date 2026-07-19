from __future__ import annotations

import re
from dataclasses import dataclass

import eu5miner.inspection as inspection

from eu5miner_gui.desktop.navigation import NavigationTarget
from eu5miner_gui.diplomacy_helpers import DiplomacyHelperInfo, DiplomacyHelperView
from eu5miner_gui.religion_helpers import ReligionHelperInfo, ReligionHelperView

_COUNT_LINE_PATTERN = re.compile(r"^(?P<label>.+): (?P<value>\d+)$")


@dataclass(frozen=True)
class LinkItemViewModel:
    text: str
    target: NavigationTarget | None = None


@dataclass(frozen=True)
class SectionViewModel:
    title: str
    items: tuple[LinkItemViewModel, ...]


@dataclass(frozen=True)
class StatViewModel:
    label: str
    value: int


@dataclass(frozen=True)
class SourceLayerViewModel:
    name: str
    kind: str
    priority: int
    root: str
    replace_paths: tuple[str, ...]


@dataclass(frozen=True)
class TextPageViewModel:
    kind: str
    title: str
    description: str
    status: str
    sections: tuple[SectionViewModel, ...]
    stats: tuple[StatViewModel, ...] = ()
    source_layers: tuple[SourceLayerViewModel, ...] = ()
    notice: str | None = None
    primary_link: NavigationTarget | None = None


@dataclass(frozen=True)
class EntitySearchRecord:
    summary: inspection.EntitySummary
    search_text: str
    source_index: int


@dataclass(frozen=True)
class EntityRowViewModel:
    name: str
    label: str
    description: str
    target: NavigationTarget


@dataclass(frozen=True)
class EntityBrowserPageViewModel:
    kind: str
    title: str
    description: str
    status: str
    system: str
    sort_mode: str
    search_text: str
    total_count: int
    visible_count: int
    rows: tuple[EntityRowViewModel, ...]
    detail: TextPageViewModel | None
    selected_entity_name: str | None
    empty_message: str | None = None
    notice: str | None = None


def build_entity_search_records(
    summaries: tuple[inspection.EntitySummary, ...],
) -> tuple[EntitySearchRecord, ...]:
    records: list[EntitySearchRecord] = []
    for index, summary in enumerate(summaries):
        search_parts = [summary.name, summary.entity_kind]
        if summary.group is not None:
            search_parts.append(summary.group)
        if summary.description is not None:
            search_parts.append(summary.description)
        records.append(
            EntitySearchRecord(
                summary=summary,
                search_text=" ".join(part.casefold() for part in search_parts),
                source_index=index,
            )
        )
    return tuple(records)


def filter_and_sort_entity_records(
    records: tuple[EntitySearchRecord, ...],
    *,
    search_text: str,
    sort_mode: str,
) -> tuple[EntitySearchRecord, ...]:
    normalized_search_text = search_text.strip().casefold()
    filtered_records = tuple(
        record
        for record in records
        if not normalized_search_text or normalized_search_text in record.search_text
    )
    if sort_mode == "source":
        return tuple(sorted(filtered_records, key=lambda record: record.source_index))
    if sort_mode == "group":
        return tuple(
            sorted(
                filtered_records,
                key=lambda record: (
                    record.summary.group or "",
                    record.summary.name,
                ),
            )
        )
    return tuple(sorted(filtered_records, key=lambda record: record.summary.name))


def build_overview_page_view_model(
    *,
    summary: inspection.InstallSummary | None,
    supported_systems: tuple[inspection.SystemInfo, ...],
    entity_systems: tuple[inspection.EntitySystemInfo, ...],
    diplomacy_helpers: tuple[DiplomacyHelperInfo, ...],
    religion_helpers: tuple[ReligionHelperInfo, ...],
    status: str,
    notice: str | None,
) -> TextPageViewModel:
    sections = [
        SectionViewModel(
            title="Supported systems",
            items=tuple(
                LinkItemViewModel(
                    text=f"{info.name}: {info.description}",
                    target=NavigationTarget.report(info.name),
                )
                for info in supported_systems
            ),
        ),
        SectionViewModel(
            title="Browsable entity systems",
            items=tuple(
                LinkItemViewModel(
                    text=f"{info.name}: {info.primary_entity_kind} - {info.description}",
                    target=NavigationTarget.entity_list(info.name),
                )
                for info in entity_systems
            ),
        ),
        SectionViewModel(
            title="Helper pages",
            items=tuple(
                [
                    LinkItemViewModel(
                        text=f"{info.name}: {info.description}",
                        target=NavigationTarget.helper(info.name),
                    )
                    for info in diplomacy_helpers
                ]
                + [
                    LinkItemViewModel(
                        text=f"{info.name}: {info.description}",
                        target=NavigationTarget.helper(info.name),
                    )
                    for info in religion_helpers
                ]
            ),
        ),
    ]
    source_layers: tuple[SourceLayerViewModel, ...] = ()
    if summary is None:
        sections.append(
            SectionViewModel(
                title="Install summary",
                items=(
                    LinkItemViewModel(
                        text="No install is loaded. Auto-discovery can fail safely.",
                    ),
                    LinkItemViewModel(
                        text=(
                            "Set a manual install root or use reload after fixing "
                            "discovery."
                        ),
                    ),
                ),
            )
        )
    else:
        sections.extend(
            (
                SectionViewModel(
                    title="Install roots",
                    items=(
                        LinkItemViewModel(text=f"Install root: {summary.root}"),
                        LinkItemViewModel(text=f"Game dir: {summary.game_dir}"),
                        LinkItemViewModel(text=f"DLC dir: {summary.dlc_dir}"),
                        LinkItemViewModel(text=f"Mod dir: {summary.mod_dir}"),
                    ),
                ),
                SectionViewModel(
                    title="Phase roots",
                    items=tuple(
                        LinkItemViewModel(text=f"{phase_root.phase.value}: {phase_root.path}")
                        for phase_root in summary.phase_roots
                    ),
                ),
                SectionViewModel(
                    title="Content sources",
                    items=tuple(
                        LinkItemViewModel(text=format_source_line(source))
                        for source in summary.sources
                    ),
                ),
            )
        )
        source_layers = tuple(
            SourceLayerViewModel(
                name=source.name,
                kind=source.kind.value,
                priority=source.priority,
                root=str(source.root),
                replace_paths=source.replace_paths,
            )
            for source in summary.sources
        )
    return TextPageViewModel(
        kind="overview",
        title="Install overview",
        description=(
            "Read-only overview of the selected install, source layers, systems, "
            "and helper coverage."
        ),
        status=status,
        sections=tuple(sections),
        source_layers=source_layers,
        notice=notice,
    )


def build_report_page_view_model(
    *,
    info: inspection.SystemInfo,
    report: inspection.SystemReport | None,
    reason: str | None,
    entity_target: NavigationTarget | None,
) -> TextPageViewModel:
    if report is None:
        return unavailable_text_page(
            kind="report",
            title=f"{info.name} system report",
            description=info.description,
            reason=reason or "No report is available.",
            primary_link=entity_target,
        )
    sections = (
        SectionViewModel(
            title="Representative files",
            items=tuple(LinkItemViewModel(text=key) for key in report.representative_keys),
        ),
        SectionViewModel(
            title="Summary",
            items=tuple(LinkItemViewModel(text=line) for line in report.summary_lines),
        ),
    )
    return TextPageViewModel(
        kind="report",
        title=f"{report.name} system report",
        description=info.description,
        status="ready",
        sections=sections,
        stats=extract_stats(report.summary_lines),
        primary_link=entity_target,
    )


def build_entity_detail_page_view_model(
    *,
    info: inspection.EntitySystemInfo,
    detail: inspection.EntityDetail | None,
    reason: str | None,
    browsable_systems: set[str],
) -> TextPageViewModel:
    if detail is None:
        return unavailable_text_page(
            kind="entity_detail",
            title=f"{info.name} entity detail",
            description=info.description,
            reason=reason or "No detail is available.",
            primary_link=NavigationTarget.entity_list(info.name),
        )
    references = tuple(
        LinkItemViewModel(
            text=(
                f"{reference.role} -> {reference.system}/{reference.entity_kind}: "
                f"{reference.target_name}"
            ),
            target=(
                NavigationTarget.entity_detail(reference.system, reference.target_name)
                if reference.system in browsable_systems
                else None
            ),
        )
        for reference in detail.references
    )
    sections = (
        SectionViewModel(
            title="Summary",
            items=(
                LinkItemViewModel(text=f"System: {detail.summary.system}"),
                LinkItemViewModel(text=f"Entity kind: {detail.summary.entity_kind}"),
                LinkItemViewModel(text=f"Name: {detail.summary.name}"),
                LinkItemViewModel(text=f"Group: {detail.summary.group or 'none'}"),
                LinkItemViewModel(
                    text=f"Description: {detail.summary.description or 'none'}"
                ),
            ),
        ),
        SectionViewModel(
            title="Fields",
            items=tuple(
                LinkItemViewModel(text=f"{field.name}: {format_browse_value(field.value)}")
                for field in detail.fields
            )
            or (LinkItemViewModel(text="No fields."),),
        ),
        SectionViewModel(
            title="References",
            items=references or (LinkItemViewModel(text="No references."),),
        ),
    )
    return TextPageViewModel(
        kind="entity_detail",
        title=f"{detail.summary.name} {detail.summary.entity_kind}",
        description=info.description,
        status="ready",
        sections=sections,
        primary_link=NavigationTarget.entity_list(info.name),
    )


def build_entity_browser_page_view_model(
    *,
    info: inspection.EntitySystemInfo,
    records: tuple[EntitySearchRecord, ...],
    total_count: int,
    search_text: str,
    sort_mode: str,
    detail: TextPageViewModel | None,
    selected_entity_name: str | None,
    reason: str | None,
) -> EntityBrowserPageViewModel:
    if reason is not None:
        return EntityBrowserPageViewModel(
            kind="entity_browser",
            title=f"{info.name} entities",
            description=info.description,
            status="unavailable",
            system=info.name,
            sort_mode=sort_mode,
            search_text=search_text,
            total_count=total_count,
            visible_count=0,
            rows=(),
            detail=None,
            selected_entity_name=None,
            empty_message=reason,
        )
    rows = tuple(
        EntityRowViewModel(
            name=record.summary.name,
            label=format_entity_summary(record.summary),
            description=record.summary.description or record.summary.entity_kind,
            target=NavigationTarget.entity_detail(info.name, record.summary.name),
        )
        for record in records
    )
    empty_message = None if rows else "No entities matched the current search."
    return EntityBrowserPageViewModel(
        kind="entity_browser",
        title=f"{info.name} entities",
        description=info.description,
        status="ready",
        system=info.name,
        sort_mode=sort_mode,
        search_text=search_text,
        total_count=total_count,
        visible_count=len(rows),
        rows=rows,
        detail=detail,
        selected_entity_name=selected_entity_name,
        empty_message=empty_message,
    )


def build_helper_page_view_model(
    *,
    info: DiplomacyHelperInfo | ReligionHelperInfo,
    view: DiplomacyHelperView | ReligionHelperView | None,
    reason: str | None,
    notice: str | None,
) -> TextPageViewModel:
    if view is None:
        return unavailable_text_page(
            kind="helper",
            title=info.title,
            description=info.description,
            reason=reason or "No helper report is available.",
            notice=notice,
        )
    sections = tuple(
        SectionViewModel(
            title=section.title,
            items=tuple(LinkItemViewModel(text=line) for line in section.lines),
        )
        for section in view.sections
    )
    summary_lines: tuple[str, ...] = ()
    for section in view.sections:
        if section.title == "Coverage summary":
            summary_lines = section.lines
            break
    return TextPageViewModel(
        kind="helper",
        title=info.title,
        description=info.description,
        status="ready",
        sections=sections,
        stats=extract_stats(summary_lines),
        notice=notice,
    )


def unavailable_text_page(
    *,
    kind: str,
    title: str,
    description: str,
    reason: str,
    notice: str | None = None,
    primary_link: NavigationTarget | None = None,
) -> TextPageViewModel:
    return TextPageViewModel(
        kind=kind,
        title=title,
        description=description,
        status="unavailable",
        sections=(
            SectionViewModel(
                title="Status",
                items=(
                    LinkItemViewModel(text="Unavailable from selected install."),
                    LinkItemViewModel(text=f"Reason: {reason}"),
                ),
            ),
        ),
        notice=notice,
        primary_link=primary_link,
    )


def extract_stats(lines: tuple[str, ...]) -> tuple[StatViewModel, ...]:
    stats: list[StatViewModel] = []
    for line in lines:
        match = _COUNT_LINE_PATTERN.match(line)
        if match is None:
            continue
        stats.append(
            StatViewModel(
                label=match.group("label"),
                value=int(match.group("value")),
            )
        )
    return tuple(stats)


def format_browse_value(value: inspection.BrowseValue) -> str:
    if isinstance(value, tuple):
        return ", ".join(value) if value else "(none)"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def format_source_line(source: inspection.InstallSourceSummary) -> str:
    replace_paths = (
        f" replace_paths={', '.join(source.replace_paths)}" if source.replace_paths else ""
    )
    return (
        f"{source.kind.value}:{source.name} priority={source.priority} root={source.root}"
        f"{replace_paths}"
    )


def format_entity_summary(summary: inspection.EntitySummary) -> str:
    line = summary.name
    if summary.group is not None:
        line = f"{line} [{summary.group}]"
    if summary.description is not None:
        line = f"{line}: {summary.description}"
    return line
