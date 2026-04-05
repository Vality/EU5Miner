"""Read-only browser shell over the stable core inspection facade."""

from __future__ import annotations

from pathlib import Path

import eu5miner.inspection as inspection

from eu5miner_gui.browser import build_browser_model, render_browser_model


def list_supported_system_names() -> tuple[str, ...]:
    return tuple(system.name for system in inspection.list_supported_systems())


def list_entity_system_names() -> tuple[str, ...]:
    return tuple(system.name for system in inspection.list_entity_systems())


def build_shell_message(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    selected_entity_system: str | None = None,
    selected_entity_name: str | None = None,
    include_all_systems: bool = False,
    language: str = "english",
) -> str:
    return render_browser_model(
        build_browser_model(
            install_root,
            selected_system=selected_system,
            selected_entity_system=selected_entity_system,
            selected_entity_name=selected_entity_name,
            include_all_systems=include_all_systems,
            language=language,
        )
    )


def launch_app(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    selected_entity_system: str | None = None,
    selected_entity_name: str | None = None,
    include_all_systems: bool = False,
    language: str = "english",
) -> str:
    return build_shell_message(
        install_root,
        selected_system=selected_system,
        selected_entity_system=selected_entity_system,
        selected_entity_name=selected_entity_name,
        include_all_systems=include_all_systems,
        language=language,
    )
