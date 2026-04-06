"""Structured read-only browser model over stable core browse seams."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path

import eu5miner.inspection as inspection
from eu5miner import GameInstall

from eu5miner_gui.diplomacy_helpers import (
    DiplomacyHelperInfo,
    build_diplomacy_helper_view,
    get_diplomacy_helper_info,
    list_diplomacy_helpers,
)
from eu5miner_gui.religion_helpers import (
    ReligionHelperInfo,
    build_religion_helper_view,
    get_religion_helper_info,
    list_religion_helpers,
)


@dataclass(frozen=True)
class BrowserSection:
    title: str
    lines: tuple[str, ...]
    use_section_line_limit: bool = True


@dataclass(frozen=True)
class BrowserPage:
    key: str
    title: str
    description: str
    status: str
    sections: tuple[BrowserSection, ...]
    navigation_hints: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrowserPageSelection:
    page_key: str
    selected_system: str | None = None
    selected_entity_system: str | None = None
    selected_entity_name: str | None = None
    selected_diplomacy_helper: str | None = None
    selected_religion_helper: str | None = None

    @property
    def requires_install(self) -> bool:
        return self.page_key != "overview"


@dataclass(frozen=True)
class BrowserSessionSummary:
    loaded_page_count: int
    ready_page_count: int
    unavailable_page_count: int
    requested_report_scope: str
    requested_entity_scope: str
    requested_entity_detail: str
    requested_diplomacy_helper_scope: str
    requested_religion_helper_scope: str
    install_summary_loaded: bool


@dataclass(frozen=True)
class BrowserModel:
    supported_systems: tuple[inspection.SystemInfo, ...]
    entity_systems: tuple[inspection.EntitySystemInfo, ...]
    diplomacy_helpers: tuple[DiplomacyHelperInfo, ...]
    religion_helpers: tuple[ReligionHelperInfo, ...]
    session_summary: BrowserSessionSummary
    pages: tuple[BrowserPage, ...]
    selected_page_key: str

    def page_keys(self) -> tuple[str, ...]:
        return tuple(page.key for page in self.pages)

    def get_page(self, key: str) -> BrowserPage | None:
        for page in self.pages:
            if page.key == key:
                return page
        return None


@dataclass(frozen=True)
class PageWindow:
    start: int
    end: int
    total: int

    @property
    def has_hidden_pages(self) -> bool:
        return self.start > 0 or self.end < self.total


def parse_browser_page_selection(page_key: str) -> BrowserPageSelection:
    normalized_page_key = page_key.strip()
    if not normalized_page_key:
        raise KeyError("Page key cannot be empty.")

    if normalized_page_key.casefold() in {"overview", "home"}:
        return BrowserPageSelection(page_key="overview")

    page_parts = normalized_page_key.split(":")
    page_prefix = page_parts[0].casefold()
    if len(page_parts) == 2 and page_prefix in {"report", "system"}:
        selected_system = page_parts[1].strip()
        if selected_system:
            return BrowserPageSelection(
                page_key=_report_page_key(selected_system),
                selected_system=selected_system,
            )
    if len(page_parts) == 2 and page_prefix in {"entities", "list"}:
        selected_entity_system = page_parts[1].strip()
        if selected_entity_system:
            return BrowserPageSelection(
                page_key=_entity_list_page_key(selected_entity_system),
                selected_entity_system=selected_entity_system,
            )
    if len(page_parts) == 2 and page_prefix in {"helper", "diplomacy-helper", "religion-helper"}:
        helper_name = page_parts[1].strip()
        if helper_name:
            if page_prefix == "religion-helper" or _is_religion_helper_name(helper_name):
                return BrowserPageSelection(
                    page_key=_religion_helper_page_key(helper_name),
                    selected_religion_helper=helper_name,
                )
            return BrowserPageSelection(
                page_key=_diplomacy_helper_page_key(helper_name),
                selected_diplomacy_helper=helper_name,
            )
    if len(page_parts) >= 3 and page_prefix in {"entity", "detail"}:
        selected_entity_system = page_parts[1].strip()
        entity_name = ":".join(page_parts[2:]).strip()
        if selected_entity_system and entity_name:
            return BrowserPageSelection(
                page_key=_entity_detail_page_key(selected_entity_system, entity_name),
                selected_entity_system=selected_entity_system,
                selected_entity_name=entity_name,
            )

    raise KeyError(
        "Unknown page key format. Valid examples: overview or home, report:map or "
        "system:map, entities:religion or list:religion, helper:war-flow or "
        "diplomacy-helper:war-flow, helper:religion-overview or "
        "religion-helper:religion-overview, entity:map:stockholm or "
        "detail:map:stockholm"
    )


def build_browser_model(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    selected_entity_system: str | None = None,
    selected_entity_name: str | None = None,
    selected_diplomacy_helper: str | None = None,
    selected_religion_helper: str | None = None,
    include_all_systems: bool = False,
    language: str = "english",
    entity_list_sort: str = "name",
    entity_list_mode: str = "compact",
    entity_list_limit: int | None = 25,
    entity_list_offset: int | None = None,
) -> BrowserModel:
    supported_systems = inspection.list_supported_systems()
    entity_systems = inspection.list_entity_systems()
    diplomacy_helpers = list_diplomacy_helpers()
    religion_helpers = list_religion_helpers()
    _validate_selected_system(supported_systems, selected_system)
    _validate_selected_entity_system(entity_systems, selected_entity_system)
    _validate_selected_entity_name(selected_entity_system, selected_entity_name)
    _validate_selected_diplomacy_helper(diplomacy_helpers, selected_diplomacy_helper)
    _validate_selected_religion_helper(religion_helpers, selected_religion_helper)
    normalized_entity_list_sort = _normalize_entity_list_sort(entity_list_sort)
    normalized_entity_list_mode = _normalize_entity_list_mode(entity_list_mode)
    normalized_entity_list_limit = _normalize_limit(
        entity_list_limit,
        option_name="entity_list_limit",
    )
    normalized_entity_list_offset = _normalize_offset(
        entity_list_offset,
        option_name="entity_list_offset",
    )

    summary: inspection.InstallSummary | None = None
    report_pages: list[BrowserPage] = []
    entity_list_pages: list[BrowserPage] = []
    entity_detail_pages: list[BrowserPage] = []
    diplomacy_helper_pages: list[BrowserPage] = []
    religion_helper_pages: list[BrowserPage] = []
    ready_report_names: tuple[str, ...] = ()
    unavailable_report_names: tuple[str, ...] = ()
    ready_entity_list_names: tuple[str, ...] = ()
    unavailable_entity_list_names: tuple[str, ...] = ()
    ready_entity_detail_names: tuple[str, ...] = ()
    unavailable_entity_detail_names: tuple[str, ...] = ()
    ready_diplomacy_helper_names: tuple[str, ...] = ()
    unavailable_diplomacy_helper_names: tuple[str, ...] = ()
    ready_religion_helper_names: tuple[str, ...] = ()
    unavailable_religion_helper_names: tuple[str, ...] = ()

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
                _build_entity_list_page(
                    install,
                    info,
                    sort_mode=normalized_entity_list_sort,
                    list_mode=normalized_entity_list_mode,
                    list_limit=normalized_entity_list_limit,
                    list_offset=normalized_entity_list_offset,
                )
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

        if selected_diplomacy_helper is not None:
            helper_page = _build_diplomacy_helper_page(install, selected_diplomacy_helper)
            diplomacy_helper_pages = [helper_page]
            if helper_page.status == "ready":
                ready_diplomacy_helper_names = (helper_page.key,)
            else:
                unavailable_diplomacy_helper_names = (helper_page.key,)

        if selected_religion_helper is not None:
            helper_page = _build_religion_helper_page(install, selected_religion_helper)
            religion_helper_pages = [helper_page]
            if helper_page.status == "ready":
                ready_religion_helper_names = (helper_page.key,)
            else:
                unavailable_religion_helper_names = (helper_page.key,)

    loaded_page_count = (
        1
        + len(report_pages)
        + len(entity_list_pages)
        + len(entity_detail_pages)
        + len(diplomacy_helper_pages)
        + len(religion_helper_pages)
    )

    ready_page_count = (
        1
        + len(ready_report_names)
        + len(ready_entity_list_names)
        + len(ready_entity_detail_names)
        + len(ready_diplomacy_helper_names)
        + len(ready_religion_helper_names)
    )
    unavailable_page_count = (
        len(unavailable_report_names)
        + len(unavailable_entity_list_names)
        + len(unavailable_entity_detail_names)
        + len(unavailable_diplomacy_helper_names)
        + len(unavailable_religion_helper_names)
    )
    session_summary = BrowserSessionSummary(
        loaded_page_count=loaded_page_count,
        ready_page_count=ready_page_count,
        unavailable_page_count=unavailable_page_count,
        requested_report_scope=(
            "all supported reports"
            if include_all_systems
            else selected_system or "overview only"
        ),
        requested_entity_scope=(
            "all covered entity lists"
            if include_all_systems
            else selected_entity_system or "none"
        ),
        requested_entity_detail=selected_entity_name or "none",
        requested_diplomacy_helper_scope=selected_diplomacy_helper or "none",
        requested_religion_helper_scope=selected_religion_helper or "none",
        install_summary_loaded=summary is not None,
    )

    overview_page = _build_overview_page(
        supported_systems,
        entity_systems,
        diplomacy_helpers,
        religion_helpers,
        summary,
        session_summary=session_summary,
        selected_system=selected_system,
        selected_entity_system=selected_entity_system,
        selected_entity_name=selected_entity_name,
        selected_diplomacy_helper=selected_diplomacy_helper,
        selected_religion_helper=selected_religion_helper,
        include_all_systems=include_all_systems,
        ready_report_names=ready_report_names,
        unavailable_report_names=unavailable_report_names,
        ready_entity_list_names=ready_entity_list_names,
        unavailable_entity_list_names=unavailable_entity_list_names,
        ready_entity_detail_names=ready_entity_detail_names,
        unavailable_entity_detail_names=unavailable_entity_detail_names,
        ready_diplomacy_helper_names=ready_diplomacy_helper_names,
        unavailable_diplomacy_helper_names=unavailable_diplomacy_helper_names,
        ready_religion_helper_names=ready_religion_helper_names,
        unavailable_religion_helper_names=unavailable_religion_helper_names,
    )
    pages = (
        overview_page,
        *report_pages,
        *entity_list_pages,
        *entity_detail_pages,
        *diplomacy_helper_pages,
        *religion_helper_pages,
    )
    selected_page_key = _resolve_selected_page_key(
        pages,
        selected_system=selected_system,
        selected_entity_system=selected_entity_system,
        selected_entity_name=selected_entity_name,
        selected_diplomacy_helper=selected_diplomacy_helper,
        selected_religion_helper=selected_religion_helper,
    )
    return BrowserModel(
        supported_systems=supported_systems,
        entity_systems=entity_systems,
        diplomacy_helpers=diplomacy_helpers,
        religion_helpers=religion_helpers,
        session_summary=session_summary,
        pages=pages,
        selected_page_key=selected_page_key,
    )


def render_browser_model(
    model: BrowserModel,
    *,
    page_key: str | None = None,
    page_filter: str | None = None,
    list_pages_only: bool = False,
    show_all_pages: bool = False,
    page_list_limit: int | None = 12,
    page_list_offset: int | None = None,
    section_line_limit: int | None = 25,
) -> str:
    normalized_page_filter = _normalize_optional_text(page_filter)
    normalized_page_list_limit = _normalize_limit(
        page_list_limit,
        option_name="page_list_limit",
    )
    normalized_page_list_offset = _normalize_offset(
        page_list_offset,
        option_name="page_list_offset",
    )
    normalized_section_line_limit = _normalize_limit(
        section_line_limit,
        option_name="section_line_limit",
    )
    session_selected_page = model.get_page(model.selected_page_key)
    visible_pages = _filter_pages(model.pages, normalized_page_filter)
    selected_page = _resolve_rendered_page(
        model,
        visible_pages,
        page_key=page_key,
        page_filter=normalized_page_filter,
    )
    indexed_pages, page_window = _window_pages(
        visible_pages,
        selected_page=selected_page,
        page_list_limit=normalized_page_list_limit,
        page_list_offset=normalized_page_list_offset,
    )
    selected_page_label = selected_page.key if selected_page is not None else "none"
    page_index_title = _format_page_index_title(
        model,
        visible_pages=visible_pages,
        page_window=page_window,
        page_filter=normalized_page_filter,
    )

    lines = [
        "EU5MinerGUI read-only browser ready.",
        "Stable inspection facade available.",
        f"Selected page: {selected_page_label}",
        *_build_session_summary_lines(
            model.session_summary,
            visible_page_count=len(visible_pages),
            page_filter=normalized_page_filter,
        ),
    ]
    if normalized_page_filter is not None:
        lines.append(f"Page filter: {normalized_page_filter}")
    lines.extend(
        (
            page_index_title,
            *(
                f"{'*' if selected_page is not None and page.key == selected_page.key else '-'} "
                f"{page.key}: {page.title}{_format_page_status_suffix(page)}"
                for page in indexed_pages
            ),
        )
    )

    if not visible_pages:
        lines.extend(
            (
                "",
                "No pages matched the current filter.",
                "Page filters only search already-loaded pages. Widen the session with "
                "--all-systems or adjust the current system/entity selection.",
                *_build_session_flow_guidance_lines(
                    visible_pages=visible_pages,
                    indexed_pages=indexed_pages,
                    session_selected_page=session_selected_page,
                    rendered_page=selected_page,
                    page_window=page_window,
                    page_filter=normalized_page_filter,
                    page_list_limit=normalized_page_list_limit,
                    page_list_offset=normalized_page_list_offset,
                ),
            )
        )
        return "\n".join(lines)

    if page_window.has_hidden_pages:
        lines.append(
            f"Page window: showing {page_window.start + 1}-{page_window.end} of "
            f"{page_window.total} matched pages."
        )
    lines.extend(
        _build_session_flow_guidance_lines(
            visible_pages=visible_pages,
            indexed_pages=indexed_pages,
            session_selected_page=session_selected_page,
            rendered_page=selected_page,
            page_window=page_window,
            page_filter=normalized_page_filter,
            page_list_limit=normalized_page_list_limit,
            page_list_offset=normalized_page_list_offset,
        )
    )

    if list_pages_only:
        lines.extend(("", "Index mode: page content hidden."))
        return "\n".join(lines)

    pages_to_render = visible_pages if show_all_pages else (selected_page,)
    for page in pages_to_render:
        if page is None:
            continue
        lines.extend(("", f"== {page.title} ==", page.description))
        navigation_lines = _build_navigation_lines(model, page)
        if navigation_lines:
            lines.append("Navigation:")
            lines.extend(f"- {line}" for line in navigation_lines)
        for section in page.sections:
            lines.append(f"{section.title}:")
            displayed_section_lines, hidden_line_count = _truncate_lines(
                section.lines,
                line_limit=(
                    normalized_section_line_limit
                    if section.use_section_line_limit
                    else None
                ),
            )
            lines.extend(f"- {line}" for line in displayed_section_lines)
            if hidden_line_count > 0:
                lines.append(
                    "- ... "
                    f"{hidden_line_count} more lines hidden; increase --section-line-limit "
                    "or use 0 for full output."
                )

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
        suggestion = _format_candidate_suggestion(selected_system, valid_system_names)
        raise KeyError(
            f"Unknown system '{selected_system}'.{suggestion} Valid systems: {valid_systems}"
        )


def _validate_selected_entity_system(
    entity_systems: tuple[inspection.EntitySystemInfo, ...],
    selected_entity_system: str | None,
) -> None:
    if selected_entity_system is None:
        return

    valid_system_names = {info.name for info in entity_systems}
    if selected_entity_system not in valid_system_names:
        valid_systems = ", ".join(sorted(valid_system_names))
        suggestion = _format_candidate_suggestion(
            selected_entity_system,
            valid_system_names,
        )
        raise KeyError(
            "Unknown entity system "
            f"'{selected_entity_system}'.{suggestion} Valid systems: {valid_systems}"
        )


def _format_candidate_suggestion(value: str, candidates: set[str]) -> str:
    matches = get_close_matches(value, sorted(candidates), n=1, cutoff=0.6)
    if not matches:
        return ""
    return f" Did you mean '{matches[0]}'?"


def _validate_selected_entity_name(
    selected_entity_system: str | None,
    selected_entity_name: str | None,
) -> None:
    if selected_entity_name is None:
        return
    if selected_entity_system is None:
        raise ValueError("An entity name requires a selected entity system.")


def _validate_selected_diplomacy_helper(
    diplomacy_helpers: tuple[DiplomacyHelperInfo, ...],
    selected_diplomacy_helper: str | None,
) -> None:
    if selected_diplomacy_helper is None:
        return

    valid_helper_names = {info.name for info in diplomacy_helpers}
    if selected_diplomacy_helper not in valid_helper_names:
        valid_helpers = ", ".join(sorted(valid_helper_names))
        suggestion = _format_candidate_suggestion(
            selected_diplomacy_helper,
            valid_helper_names,
        )
        raise KeyError(
            "Unknown diplomacy helper "
            f"'{selected_diplomacy_helper}'.{suggestion} Valid helpers: {valid_helpers}"
        )


def _validate_selected_religion_helper(
    religion_helpers: tuple[ReligionHelperInfo, ...],
    selected_religion_helper: str | None,
) -> None:
    if selected_religion_helper is None:
        return

    valid_helper_names = {info.name for info in religion_helpers}
    if selected_religion_helper not in valid_helper_names:
        valid_helpers = ", ".join(sorted(valid_helper_names))
        suggestion = _format_candidate_suggestion(
            selected_religion_helper,
            valid_helper_names,
        )
        raise KeyError(
            "Unknown religion helper "
            f"'{selected_religion_helper}'.{suggestion} Valid helpers: {valid_helpers}"
        )


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
    diplomacy_helpers: tuple[DiplomacyHelperInfo, ...],
    religion_helpers: tuple[ReligionHelperInfo, ...],
    summary: inspection.InstallSummary | None,
    *,
    session_summary: BrowserSessionSummary,
    selected_system: str | None,
    selected_entity_system: str | None,
    selected_entity_name: str | None,
    selected_diplomacy_helper: str | None,
    selected_religion_helper: str | None,
    include_all_systems: bool,
    ready_report_names: tuple[str, ...],
    unavailable_report_names: tuple[str, ...],
    ready_entity_list_names: tuple[str, ...],
    unavailable_entity_list_names: tuple[str, ...],
    ready_entity_detail_names: tuple[str, ...],
    unavailable_entity_detail_names: tuple[str, ...],
    ready_diplomacy_helper_names: tuple[str, ...],
    unavailable_diplomacy_helper_names: tuple[str, ...],
    ready_religion_helper_names: tuple[str, ...],
    unavailable_religion_helper_names: tuple[str, ...],
) -> BrowserPage:
    sections = [
        BrowserSection(
            title="Browser status",
            lines=(
                (
                    "Loaded pages: "
                    f"{session_summary.loaded_page_count} total, "
                    f"{session_summary.ready_page_count} ready, "
                    f"{session_summary.unavailable_page_count} unavailable"
                ),
                f"Requested report scope: {session_summary.requested_report_scope}",
                f"Requested entity scope: {session_summary.requested_entity_scope}",
                f"Requested entity detail: {session_summary.requested_entity_detail}",
                "Requested diplomacy helper scope: "
                f"{session_summary.requested_diplomacy_helper_scope}",
                "Requested religion helper scope: "
                f"{session_summary.requested_religion_helper_scope}",
                (
                    "Install summary loaded: "
                    f"{'yes' if session_summary.install_summary_loaded else 'no'}"
                ),
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
                (
                    "Ready diplomacy helper pages: "
                    f"{_format_page_name_list(ready_diplomacy_helper_names)}"
                ),
                (
                    "Unavailable diplomacy helper pages: "
                    f"{_format_page_name_list(unavailable_diplomacy_helper_names)}"
                ),
                (
                    "Ready religion helper pages: "
                    f"{_format_page_name_list(ready_religion_helper_names)}"
                ),
                (
                    "Unavailable religion helper pages: "
                    f"{_format_page_name_list(unavailable_religion_helper_names)}"
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
        BrowserSection(
            title="Diplomacy helper pages",
            lines=tuple(f"{info.name}: {info.description}" for info in diplomacy_helpers),
        ),
        BrowserSection(
            title="Religion helper pages",
            lines=tuple(f"{info.name}: {info.description}" for info in religion_helpers),
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
        if selected_diplomacy_helper is not None:
            unavailable_lines.append("Diplomacy helper pages require an install root.")
        if selected_religion_helper is not None:
            unavailable_lines.append("Religion helper pages require an install root.")
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
            "Browse one install summary, stable inspection-backed report and entity pages, "
            "plus thin diplomacy and religion helper pages over grouped core seams."
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
    *,
    sort_mode: str,
    list_mode: str,
    list_limit: int | None,
    list_offset: int | None,
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

    sorted_entities = _sort_entity_summaries(entities, sort_mode=sort_mode)
    visible_entities, entity_window = _window_entity_summaries(
        sorted_entities,
        list_limit=list_limit,
        list_offset=list_offset,
    )
    navigation_hints = [f"Detail page pattern: entity:{info.name}:<entity-name>"]
    if visible_entities:
        example_keys = ", ".join(
            _entity_detail_page_key(info.name, entity.name)
            for entity in visible_entities[:3]
        )
        navigation_hints.append(f"Visible detail-page examples: {example_keys}")

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
                    f"Entity count: {len(sorted_entities)}",
                    f"Sort: {sort_mode}",
                    f"List mode: {list_mode}",
                    _format_entity_window(entity_window),
                ),
            ),
            BrowserSection(
                title="Entities",
                lines=tuple(
                    _format_entity_summary(
                        entity,
                        mode=list_mode,
                        detail_page_key=_entity_detail_page_key(info.name, entity.name),
                    )
                    for entity in visible_entities
                ),
                use_section_line_limit=False,
            ),
        ),
        navigation_hints=tuple(navigation_hints),
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


def _build_diplomacy_helper_page(
    install: GameInstall,
    helper_name: str,
) -> BrowserPage:
    info = _diplomacy_helper_info(helper_name)
    try:
        helper_view = build_diplomacy_helper_view(install, helper_name)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return _build_unavailable_diplomacy_helper_page(info, str(exc))

    return BrowserPage(
        key=_diplomacy_helper_page_key(helper_view.info.name),
        title=helper_view.info.title,
        description=helper_view.info.description,
        status="ready",
        sections=tuple(
            BrowserSection(
                title=section.title,
                lines=section.lines,
                use_section_line_limit=section.use_section_line_limit,
            )
            for section in helper_view.sections
        ),
        navigation_hints=helper_view.navigation_hints,
    )


def _build_religion_helper_page(
    install: GameInstall,
    helper_name: str,
) -> BrowserPage:
    info = _religion_helper_info(helper_name)
    try:
        helper_view = build_religion_helper_view(install, helper_name)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return _build_unavailable_religion_helper_page(info, str(exc))

    return BrowserPage(
        key=_religion_helper_page_key(helper_view.info.name),
        title=helper_view.info.title,
        description=helper_view.info.description,
        status="ready",
        sections=tuple(
            BrowserSection(
                title=section.title,
                lines=section.lines,
                use_section_line_limit=section.use_section_line_limit,
            )
            for section in helper_view.sections
        ),
        navigation_hints=helper_view.navigation_hints,
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
                lines=_unavailable_page_status_lines(reason),
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
                lines=_unavailable_page_status_lines(reason),
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
                lines=_unavailable_page_status_lines(reason),
            ),
        ),
    )


def _build_unavailable_diplomacy_helper_page(
    info: DiplomacyHelperInfo,
    reason: str,
) -> BrowserPage:
    return BrowserPage(
        key=_diplomacy_helper_page_key(info.name),
        title=info.title,
        description=info.description,
        status="unavailable",
        sections=(
            BrowserSection(
                title="Status",
                lines=_unavailable_page_status_lines(reason),
            ),
        ),
    )


def _build_unavailable_religion_helper_page(
    info: ReligionHelperInfo,
    reason: str,
) -> BrowserPage:
    return BrowserPage(
        key=_religion_helper_page_key(info.name),
        title=info.title,
        description=info.description,
        status="unavailable",
        sections=(
            BrowserSection(
                title="Status",
                lines=_unavailable_page_status_lines(reason),
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


def _diplomacy_helper_info(selected_diplomacy_helper: str) -> DiplomacyHelperInfo:
    helper_info = get_diplomacy_helper_info(selected_diplomacy_helper)
    if helper_info is None:
        raise AssertionError(selected_diplomacy_helper)
    return helper_info


def _religion_helper_info(selected_religion_helper: str) -> ReligionHelperInfo:
    helper_info = get_religion_helper_info(selected_religion_helper)
    if helper_info is None:
        raise AssertionError(selected_religion_helper)
    return helper_info


def _report_page_key(system: str) -> str:
    return f"report:{system}"


def _entity_list_page_key(system: str) -> str:
    return f"entities:{system}"


def _entity_detail_page_key(system: str, entity_name: str) -> str:
    return f"entity:{system}:{entity_name}"


def _helper_page_key(helper_name: str) -> str:
    return f"helper:{helper_name}"


def _diplomacy_helper_page_key(helper_name: str) -> str:
    return _helper_page_key(helper_name)


def _religion_helper_page_key(helper_name: str) -> str:
    return _helper_page_key(helper_name)


def _is_religion_helper_name(helper_name: str) -> bool:
    return get_religion_helper_info(helper_name) is not None or helper_name.startswith(
        "religion-"
    )


def _format_entity_summary(
    summary: inspection.EntitySummary,
    *,
    mode: str = "compact",
    detail_page_key: str | None = None,
) -> str:
    line = summary.name
    if summary.group is not None:
        line = f"{line} [{summary.group}]"
    if summary.description is not None:
        line = f"{line}: {summary.description}"
    if mode == "detail" and detail_page_key is not None:
        line = f"{line} | page: {detail_page_key}"
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


def _unavailable_page_status_lines(reason: str) -> tuple[str, ...]:
    return (
        "Unavailable from selected install.",
        f"Reason: {reason}",
        "Check the overview page for install roots and loaded content sources.",
        (
            "Unavailable pages stay indexed so partial or synthetic installs keep a "
            "stable session."
        ),
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None


def _normalize_entity_list_sort(value: str) -> str:
    normalized_value = value.strip().casefold()
    valid_values = {"name", "group", "source"}
    if normalized_value not in valid_values:
        valid_value_list = ", ".join(sorted(valid_values))
        raise ValueError(
            f"entity_list_sort must be one of: {valid_value_list}."
        )
    return normalized_value


def _normalize_entity_list_mode(value: str) -> str:
    normalized_value = value.strip().casefold()
    valid_values = {"compact", "detail"}
    if normalized_value not in valid_values:
        valid_value_list = ", ".join(sorted(valid_values))
        raise ValueError(
            f"entity_list_mode must be one of: {valid_value_list}."
        )
    return normalized_value


def _filter_pages(
    pages: tuple[BrowserPage, ...],
    page_filter: str | None,
) -> tuple[BrowserPage, ...]:
    if page_filter is None:
        return pages

    normalized_filter = page_filter.casefold()
    return tuple(page for page in pages if _page_matches_filter(page, normalized_filter))


def _page_matches_filter(page: BrowserPage, normalized_filter: str) -> bool:
    page_text = [page.key, page.title, page.description]
    for section in page.sections:
        page_text.append(section.title)
        page_text.extend(section.lines)
    return any(normalized_filter in line.casefold() for line in page_text)


def _normalize_limit(value: int | None, *, option_name: str) -> int | None:
    if value is None or value == 0:
        return None
    if value < 0:
        raise ValueError(f"{option_name} cannot be negative.")
    return value


def _normalize_offset(value: int | None, *, option_name: str) -> int | None:
    if value is None:
        return None
    if value < 0:
        raise ValueError(f"{option_name} cannot be negative.")
    return value


def _window_pages(
    visible_pages: tuple[BrowserPage, ...],
    *,
    selected_page: BrowserPage | None,
    page_list_limit: int | None,
    page_list_offset: int | None,
) -> tuple[tuple[BrowserPage, ...], PageWindow]:
    total = len(visible_pages)
    if total == 0:
        return (), PageWindow(start=0, end=0, total=0)

    if page_list_limit is None or page_list_limit >= total:
        return visible_pages, PageWindow(start=0, end=total, total=total)

    max_start = total - page_list_limit
    if page_list_offset is not None:
        start = min(page_list_offset, max_start)
    elif selected_page is not None:
        selected_index = visible_pages.index(selected_page)
        start = min(selected_index, max_start)
    else:
        start = 0

    end = start + page_list_limit
    return visible_pages[start:end], PageWindow(start=start, end=end, total=total)


def _format_page_index_title(
    model: BrowserModel,
    *,
    visible_pages: tuple[BrowserPage, ...],
    page_window: PageWindow,
    page_filter: str | None,
) -> str:
    if not visible_pages:
        if page_filter is None:
            return "Available pages:"
        return f"Available pages (0 of {len(model.pages)} loaded):"

    if page_filter is not None and page_window.has_hidden_pages:
        return (
            f"Available pages (showing {page_window.start + 1}-{page_window.end} of "
            f"{len(visible_pages)} matched, {len(model.pages)} loaded):"
        )
    if page_filter is not None:
        return f"Available pages ({len(visible_pages)} of {len(model.pages)} loaded):"
    if page_window.has_hidden_pages:
        return (
            f"Available pages (showing {page_window.start + 1}-{page_window.end} of "
            f"{len(visible_pages)} loaded):"
        )
    return "Available pages:"


def _build_session_summary_lines(
    session_summary: BrowserSessionSummary,
    *,
    visible_page_count: int,
    page_filter: str | None,
) -> tuple[str, ...]:
    lines = [
        (
            "Session summary: "
            f"{session_summary.loaded_page_count} loaded, "
            f"{session_summary.ready_page_count} ready, "
            f"{session_summary.unavailable_page_count} unavailable; "
            "install summary loaded: "
            f"{'yes' if session_summary.install_summary_loaded else 'no'}"
        ),
        (
            "Session request: "
            f"reports={session_summary.requested_report_scope}; "
            f"entity lists={session_summary.requested_entity_scope}; "
            f"detail={session_summary.requested_entity_detail}"
        ),
        f"Session diplomacy helpers: {session_summary.requested_diplomacy_helper_scope}",
        f"Session religion helpers: {session_summary.requested_religion_helper_scope}",
    ]
    if page_filter is not None:
        lines.append(
            "Filter result: "
            f"{visible_page_count} matched of {session_summary.loaded_page_count} loaded pages"
        )
    return tuple(lines)


def _build_session_flow_guidance_lines(
    *,
    visible_pages: tuple[BrowserPage, ...],
    indexed_pages: tuple[BrowserPage, ...],
    session_selected_page: BrowserPage | None,
    rendered_page: BrowserPage | None,
    page_window: PageWindow,
    page_filter: str | None,
    page_list_limit: int | None,
    page_list_offset: int | None,
) -> tuple[str, ...]:
    lines: list[str] = []

    if (
        page_filter is not None
        and session_selected_page is not None
        and session_selected_page not in visible_pages
    ):
        lines.extend(
            (
                f"Session-selected page hidden by current filter: {session_selected_page.key}.",
                f"Direct page flag: --page {session_selected_page.key}",
                "Filter reopen hint: clear --page-filter or change it until that page is "
                "visible again.",
            )
        )

    if (
        rendered_page is not None
        and page_window.has_hidden_pages
        and rendered_page not in indexed_pages
    ):
        lines.extend(
            (
                f"Selected page is outside the current page window: {rendered_page.key}.",
                f"Direct page flag: --page {rendered_page.key}",
                _format_page_window_reopen_hint(
                    visible_pages,
                    rendered_page=rendered_page,
                    page_list_limit=page_list_limit,
                    page_list_offset=page_list_offset,
                ),
                "Full index hint: use --page-list-limit 0 to disable page-index windowing.",
            )
        )

    return tuple(lines)


def _format_page_window_reopen_hint(
    visible_pages: tuple[BrowserPage, ...],
    *,
    rendered_page: BrowserPage,
    page_list_limit: int | None,
    page_list_offset: int | None,
) -> str:
    if page_list_limit is None:
        return (
            "Index reopen hint: remove the explicit page window to keep the selected "
            "page visible."
        )

    recommended_offset = _recommended_page_list_offset(
        visible_pages,
        selected_page=rendered_page,
        page_list_limit=page_list_limit,
    )
    if page_list_offset is None:
        return (
            "Index reopen hint: omit --page-list-offset to keep the selected page "
            "visible."
        )
    return (
        "Index reopen hint: omit --page-list-offset to keep the selected page visible, "
        f"or use --page-list-offset {recommended_offset}."
    )


def _recommended_page_list_offset(
    visible_pages: tuple[BrowserPage, ...],
    *,
    selected_page: BrowserPage,
    page_list_limit: int,
) -> int:
    selected_index = visible_pages.index(selected_page)
    max_start = max(0, len(visible_pages) - page_list_limit)
    return min(selected_index, max_start)


def _build_navigation_lines(model: BrowserModel, page: BrowserPage) -> tuple[str, ...]:
    page_index = model.pages.index(page)
    lines = [
        f"Page key: {page.key}",
        f"Direct page flag: --page {page.key}",
        f"Session position: {page_index + 1} of {len(model.pages)} loaded pages",
    ]
    if page_index > 0:
        lines.append(f"Previous page: {model.pages[page_index - 1].key}")
    if page_index + 1 < len(model.pages):
        lines.append(f"Next page: {model.pages[page_index + 1].key}")
    if page.key == "overview":
        return tuple(lines)

    if model.get_page("overview") is not None:
        lines.append("Overview page: overview")

    if page.key.startswith("entities:"):
        _, system = page.key.split(":", maxsplit=1)
        lines.append(f"Selection flags: --entity-system {system}")
        lines.append(f"Detail page pattern: entity:{system}:<entity-name>")
    elif page.key.startswith("entity:"):
        _, system, entity_name = page.key.split(":", maxsplit=2)
        list_key = _entity_list_page_key(system)
        lines.append(
            "Selection flags: "
            f"--entity-system {system} --entity {_format_cli_value(entity_name)}"
        )
        if model.get_page(list_key) is not None:
            lines.append(f"Parent list page: {list_key}")
    elif page.key.startswith("report:"):
        _, system = page.key.split(":", maxsplit=1)
        lines.append(f"Selection flags: --system {system}")
        list_key = _entity_list_page_key(system)
        if model.get_page(list_key) is not None:
            lines.append(f"Related entity list page: {list_key}")
    elif page.key.startswith("helper:"):
        _, helper_name = page.key.split(":", maxsplit=1)
        if _is_religion_helper_name(helper_name):
            lines.append(f"Selection flags: --religion-helper {helper_name}")
            report_key = _report_page_key("religion")
        else:
            lines.append(f"Selection flags: --diplomacy-helper {helper_name}")
            report_key = _report_page_key("diplomacy")
        if model.get_page(report_key) is not None:
            lines.append(f"Related system report page: {report_key}")

    lines.extend(page.navigation_hints)

    return tuple(lines)


def _format_cli_value(value: str) -> str:
    if not value or any(character.isspace() for character in value):
        escaped_value = value.replace('"', '\\"')
        return f'"{escaped_value}"'
    return value


def _sort_entity_summaries(
    entities: tuple[inspection.EntitySummary, ...],
    *,
    sort_mode: str,
) -> tuple[inspection.EntitySummary, ...]:
    if sort_mode == "source":
        return entities
    if sort_mode == "name":
        return tuple(sorted(entities, key=lambda entity: entity.name.casefold()))
    return tuple(
        sorted(
            entities,
            key=lambda entity: (
                (entity.group or "").casefold(),
                entity.name.casefold(),
            ),
        )
    )


def _window_entity_summaries(
    entities: tuple[inspection.EntitySummary, ...],
    *,
    list_limit: int | None,
    list_offset: int | None,
) -> tuple[tuple[inspection.EntitySummary, ...], PageWindow]:
    total = len(entities)
    if total == 0:
        return (), PageWindow(start=0, end=0, total=0)

    if list_limit is None or list_limit >= total:
        return entities, PageWindow(start=0, end=total, total=total)

    max_start = total - list_limit
    start = min(list_offset or 0, max_start)
    end = start + list_limit
    return entities[start:end], PageWindow(start=start, end=end, total=total)


def _format_entity_window(entity_window: PageWindow) -> str:
    if entity_window.total == 0:
        return "Entity window: none"
    return (
        f"Entity window: showing {entity_window.start + 1}-{entity_window.end} of "
        f"{entity_window.total}"
    )


def _truncate_lines(
    lines: tuple[str, ...],
    *,
    line_limit: int | None,
) -> tuple[tuple[str, ...], int]:
    if line_limit is None or len(lines) <= line_limit:
        return lines, 0
    return lines[:line_limit], len(lines) - line_limit


def _resolve_rendered_page(
    model: BrowserModel,
    visible_pages: tuple[BrowserPage, ...],
    *,
    page_key: str | None,
    page_filter: str | None,
) -> BrowserPage | None:
    visible_page_keys = {page.key for page in visible_pages}

    if page_key is not None:
        requested_page = model.get_page(page_key)
        if requested_page is None:
            raise KeyError(
                f"Unknown page key '{page_key}'. Available pages: "
                f"{', '.join(model.page_keys())}"
            )
        if requested_page.key not in visible_page_keys:
            if page_filter is None:
                raise KeyError(f"Page key '{page_key}' is not loaded in the current session.")
            raise KeyError(
                f"Page key '{page_key}' does not match page filter '{page_filter}'."
            )
        return requested_page

    default_page = model.get_page(model.selected_page_key)
    if default_page is not None and default_page.key in visible_page_keys:
        return default_page
    if visible_pages:
        return visible_pages[0]
    return None


def _resolve_selected_page_key(
    pages: tuple[BrowserPage, ...],
    *,
    selected_system: str | None,
    selected_entity_system: str | None,
    selected_entity_name: str | None,
    selected_diplomacy_helper: str | None,
    selected_religion_helper: str | None,
) -> str:
    page_keys = {page.key for page in pages}

    if selected_entity_system is not None and selected_entity_name is not None:
        detail_key = _entity_detail_page_key(selected_entity_system, selected_entity_name)
        if detail_key in page_keys:
            return detail_key

    if selected_religion_helper is not None:
        helper_key = _religion_helper_page_key(selected_religion_helper)
        if helper_key in page_keys:
            return helper_key

    if selected_diplomacy_helper is not None:
        helper_key = _diplomacy_helper_page_key(selected_diplomacy_helper)
        if helper_key in page_keys:
            return helper_key

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
