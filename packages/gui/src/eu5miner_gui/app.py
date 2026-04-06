"""Read-only browser shell over stable core browse seams."""

from __future__ import annotations

from pathlib import Path

import eu5miner.inspection as inspection

from eu5miner_gui.browser import (
    build_browser_model,
    parse_browser_page_selection,
    render_browser_model,
)
from eu5miner_gui.desktop.bootstrap import DesktopLaunchOptions, launch_desktop_app
from eu5miner_gui.desktop.navigation import NavigationTarget, navigation_target_from_page_key
from eu5miner_gui.diplomacy_helpers import list_diplomacy_helpers
from eu5miner_gui.religion_helpers import list_religion_helpers


def list_supported_system_names() -> tuple[str, ...]:
    return tuple(system.name for system in inspection.list_supported_systems())


def list_entity_system_names() -> tuple[str, ...]:
    return tuple(system.name for system in inspection.list_entity_systems())


def list_diplomacy_helper_names() -> tuple[str, ...]:
    return tuple(helper.name for helper in list_diplomacy_helpers())


def list_religion_helper_names() -> tuple[str, ...]:
    return tuple(helper.name for helper in list_religion_helpers())


def build_shell_message(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    selected_entity_system: str | None = None,
    selected_entity_name: str | None = None,
    selected_diplomacy_helper: str | None = None,
    selected_religion_helper: str | None = None,
    include_all_systems: bool = False,
    language: str = "english",
    page_key: str | None = None,
    page_filter: str | None = None,
    list_pages_only: bool = False,
    show_all_pages: bool = False,
    page_list_limit: int | None = 12,
    page_list_offset: int | None = None,
    section_line_limit: int | None = 25,
    entity_list_sort: str = "name",
    entity_list_mode: str = "compact",
    entity_list_limit: int | None = 25,
    entity_list_offset: int | None = None,
) -> str:
    (
        normalized_page_key,
        selected_system,
        selected_entity_system,
        selected_entity_name,
        selected_diplomacy_helper,
        selected_religion_helper,
    ) = _resolve_navigation_request(
        install_root,
        page_key=page_key,
        selected_system=selected_system,
        selected_entity_system=selected_entity_system,
        selected_entity_name=selected_entity_name,
        selected_diplomacy_helper=selected_diplomacy_helper,
        selected_religion_helper=selected_religion_helper,
    )
    return render_browser_model(
        build_browser_model(
            install_root,
            selected_system=selected_system,
            selected_entity_system=selected_entity_system,
            selected_entity_name=selected_entity_name,
            selected_diplomacy_helper=selected_diplomacy_helper,
            selected_religion_helper=selected_religion_helper,
            include_all_systems=include_all_systems,
            language=language,
            entity_list_sort=entity_list_sort,
            entity_list_mode=entity_list_mode,
            entity_list_limit=entity_list_limit,
            entity_list_offset=entity_list_offset,
        ),
        page_key=normalized_page_key,
        page_filter=page_filter,
        list_pages_only=list_pages_only,
        show_all_pages=show_all_pages,
        page_list_limit=page_list_limit,
        page_list_offset=page_list_offset,
        section_line_limit=section_line_limit,
    )


def launch_app(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    selected_entity_system: str | None = None,
    selected_entity_name: str | None = None,
    selected_diplomacy_helper: str | None = None,
    selected_religion_helper: str | None = None,
    include_all_systems: bool = False,
    language: str = "english",
    page_key: str | None = None,
    page_filter: str | None = None,
    list_pages_only: bool = False,
    show_all_pages: bool = False,
    page_list_limit: int | None = 12,
    page_list_offset: int | None = None,
    section_line_limit: int | None = 25,
    entity_list_sort: str = "name",
    entity_list_mode: str = "compact",
    entity_list_limit: int | None = 25,
    entity_list_offset: int | None = None,
) -> str:
    return build_shell_message(
        install_root,
        selected_system=selected_system,
        selected_entity_system=selected_entity_system,
        selected_entity_name=selected_entity_name,
        selected_diplomacy_helper=selected_diplomacy_helper,
        selected_religion_helper=selected_religion_helper,
        include_all_systems=include_all_systems,
        language=language,
        page_key=page_key,
        page_filter=page_filter,
        list_pages_only=list_pages_only,
        show_all_pages=show_all_pages,
        page_list_limit=page_list_limit,
        page_list_offset=page_list_offset,
        section_line_limit=section_line_limit,
        entity_list_sort=entity_list_sort,
        entity_list_mode=entity_list_mode,
        entity_list_limit=entity_list_limit,
        entity_list_offset=entity_list_offset,
    )


def build_navigation_target(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    selected_entity_system: str | None = None,
    selected_entity_name: str | None = None,
    selected_diplomacy_helper: str | None = None,
    selected_religion_helper: str | None = None,
    page_key: str | None = None,
) -> NavigationTarget:
    (
        normalized_page_key,
        resolved_system,
        resolved_entity_system,
        resolved_entity_name,
        resolved_diplomacy_helper,
        resolved_religion_helper,
    ) = _resolve_navigation_request(
        install_root,
        page_key=page_key,
        selected_system=selected_system,
        selected_entity_system=selected_entity_system,
        selected_entity_name=selected_entity_name,
        selected_diplomacy_helper=selected_diplomacy_helper,
        selected_religion_helper=selected_religion_helper,
    )
    if normalized_page_key is not None:
        return navigation_target_from_page_key(normalized_page_key)
    if resolved_entity_system is not None and resolved_entity_name is not None:
        return NavigationTarget.entity_detail(resolved_entity_system, resolved_entity_name)
    if resolved_entity_system is not None:
        return NavigationTarget.entity_list(resolved_entity_system)
    if resolved_system is not None:
        return NavigationTarget.report(resolved_system)
    if resolved_religion_helper is not None:
        return NavigationTarget.helper(resolved_religion_helper)
    if resolved_diplomacy_helper is not None:
        return NavigationTarget.helper(resolved_diplomacy_helper)
    return NavigationTarget.overview()


def launch_desktop(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    selected_entity_system: str | None = None,
    selected_entity_name: str | None = None,
    selected_diplomacy_helper: str | None = None,
    selected_religion_helper: str | None = None,
    page_key: str | None = None,
    mod_roots: tuple[str | Path, ...] = (),
) -> int:
    normalized_install_root = None if install_root is None else Path(install_root)
    normalized_mod_roots = tuple(Path(mod_root) for mod_root in mod_roots)
    initial_target = build_navigation_target(
        normalized_install_root,
        selected_system=selected_system,
        selected_entity_system=selected_entity_system,
        selected_entity_name=selected_entity_name,
        selected_diplomacy_helper=selected_diplomacy_helper,
        selected_religion_helper=selected_religion_helper,
        page_key=page_key,
    )
    return launch_desktop_app(
        options=DesktopLaunchOptions(
            install_root=normalized_install_root,
            initial_target=initial_target,
            mod_folders=normalized_mod_roots,
        )
    )


def _resolve_navigation_request(
    install_root: str | Path | None,
    *,
    page_key: str | None,
    selected_system: str | None,
    selected_entity_system: str | None,
    selected_entity_name: str | None,
    selected_diplomacy_helper: str | None,
    selected_religion_helper: str | None,
) -> tuple[str | None, str | None, str | None, str | None, str | None, str | None]:
    requested_page_key = _normalize_optional_text(page_key)
    if requested_page_key is None:
        return (
            None,
            selected_system,
            selected_entity_system,
            selected_entity_name,
            selected_diplomacy_helper,
            selected_religion_helper,
        )

    page_selection = parse_browser_page_selection(requested_page_key)
    if page_selection.requires_install and install_root is None:
        raise ValueError(f"Page key '{requested_page_key}' requires an install root.")

    _validate_navigation_conflict(
        requested_page_key,
        option_name="system",
        explicit_value=selected_system,
        page_value=page_selection.selected_system,
    )
    _validate_navigation_conflict(
        requested_page_key,
        option_name="entity-system",
        explicit_value=selected_entity_system,
        page_value=page_selection.selected_entity_system,
    )
    _validate_navigation_conflict(
        requested_page_key,
        option_name="entity",
        explicit_value=selected_entity_name,
        page_value=page_selection.selected_entity_name,
    )
    _validate_navigation_conflict(
        requested_page_key,
        option_name="diplomacy-helper",
        explicit_value=selected_diplomacy_helper,
        page_value=page_selection.selected_diplomacy_helper,
    )
    _validate_navigation_conflict(
        requested_page_key,
        option_name="religion-helper",
        explicit_value=selected_religion_helper,
        page_value=page_selection.selected_religion_helper,
    )

    return (
        page_selection.page_key,
        selected_system or page_selection.selected_system,
        selected_entity_system or page_selection.selected_entity_system,
        selected_entity_name or page_selection.selected_entity_name,
        selected_diplomacy_helper or page_selection.selected_diplomacy_helper,
        selected_religion_helper or page_selection.selected_religion_helper,
    )


def _validate_navigation_conflict(
    page_key: str,
    *,
    option_name: str,
    explicit_value: str | None,
    page_value: str | None,
) -> None:
    if explicit_value is None or page_value is None or explicit_value == page_value:
        return
    raise ValueError(
        f"Page key '{page_key}' conflicts with --{option_name}={explicit_value}."
    )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
