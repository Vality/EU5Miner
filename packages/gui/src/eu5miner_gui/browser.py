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
    pages: tuple[BrowserPage, ...]
    selected_page_key: str

    def page_keys(self) -> tuple[str, ...]:
        return tuple(page.key for page in self.pages)


def build_browser_model(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    include_all_systems: bool = False,
    language: str = "english",
) -> BrowserModel:
    supported_systems = inspection.list_supported_systems()
    _validate_selected_system(supported_systems, selected_system)

    summary: inspection.InstallSummary | None = None
    report_pages: list[BrowserPage] = []
    ready_report_names: tuple[str, ...] = ()
    unavailable_report_names: tuple[str, ...] = ()

    if install_root is not None:
        summary = inspection.inspect_install(install_root)
        systems_to_load = _resolve_systems_to_load(
            supported_systems,
            selected_system=selected_system,
            include_all_systems=include_all_systems,
        )
        if systems_to_load:
            install = GameInstall.discover(summary.root)
            report_pages = [
                _build_report_page(install, info, language=language)
                for info in supported_systems
                if info.name in systems_to_load
            ]
            ready_report_names = tuple(page.key for page in report_pages if page.status == "ready")
            unavailable_report_names = tuple(
                page.key for page in report_pages if page.status != "ready"
            )

    overview_page = _build_overview_page(
        supported_systems,
        summary,
        selected_system=selected_system,
        include_all_systems=include_all_systems,
        ready_report_names=ready_report_names,
        unavailable_report_names=unavailable_report_names,
    )
    pages = (overview_page, *report_pages)
    selected_page_key = _resolve_selected_page_key(pages, selected_system)
    return BrowserModel(
        supported_systems=supported_systems,
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


def _build_overview_page(
    supported_systems: tuple[inspection.SystemInfo, ...],
    summary: inspection.InstallSummary | None,
    *,
    selected_system: str | None,
    include_all_systems: bool,
    ready_report_names: tuple[str, ...],
    unavailable_report_names: tuple[str, ...],
) -> BrowserPage:
    requested_scope = (
        "all supported reports"
        if include_all_systems
        else selected_system or "overview only"
    )
    sections = [
        BrowserSection(
            title="Browser status",
            lines=(
                f"Requested scope: {requested_scope}",
                f"Install summary loaded: {'yes' if summary is not None else 'no'}",
                (
                    "Ready report pages: "
                    f"{', '.join(ready_report_names) if ready_report_names else 'none'}"
                ),
                (
                    "Unavailable report pages: "
                    f"{', '.join(unavailable_report_names) if unavailable_report_names else 'none'}"
                ),
            ),
        ),
        BrowserSection(
            title="Supported systems",
            lines=tuple(f"{info.name}: {info.description}" for info in supported_systems),
        ),
    ]

    if summary is None:
        unavailable_lines = ["Not loaded."]
        if selected_system is not None or include_all_systems:
            unavailable_lines.append("System reports require an install root.")
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
        description="Browse one install summary and the stable system-report entrypoints.",
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

    return _build_system_page(info, report)


def _build_system_page(
    info: inspection.SystemInfo,
    report: inspection.SystemReport,
) -> BrowserPage:
    return BrowserPage(
        key=report.name,
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


def _build_unavailable_system_page(info: inspection.SystemInfo, reason: str) -> BrowserPage:
    return BrowserPage(
        key=info.name,
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


def _format_source_summary(source: inspection.InstallSourceSummary) -> str:
    replace_paths = (
        f" replace_paths={', '.join(source.replace_paths)}" if source.replace_paths else ""
    )
    return (
        f"{source.kind.value}:{source.name} priority={source.priority} root={source.root}"
        f"{replace_paths}"
    )


def _resolve_selected_page_key(
    pages: tuple[BrowserPage, ...],
    selected_system: str | None,
) -> str:
    if selected_system is None:
        return "overview"

    page_keys = {page.key for page in pages}
    return selected_system if selected_system in page_keys else "overview"


def _format_page_status_suffix(page: BrowserPage) -> str:
    if page.status == "ready":
        return ""
    return f" ({page.status})"