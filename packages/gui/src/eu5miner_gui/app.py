"""Read-only GUI shell over the stable core inspection facade."""

from __future__ import annotations

from pathlib import Path

import eu5miner.inspection as inspection
from eu5miner import GameInstall


def list_supported_system_names() -> tuple[str, ...]:
    return tuple(system.name for system in inspection.list_supported_systems())


def build_shell_message(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    language: str = "english",
) -> str:
    lines = [
        "EU5MinerGUI read-only shell ready.",
        "Stable inspection facade available.",
        "Supported systems:",
        *(
            f"- {system.name}: {system.description}"
            for system in inspection.list_supported_systems()
        ),
    ]

    if install_root is None:
        lines.append("Install summary: not loaded.")
        if selected_system is not None:
            lines.append("Selected system report: unavailable without an install root.")
        return "\n".join(lines)

    summary = inspection.inspect_install(install_root)
    lines.extend(("", inspection.format_install_summary(summary)))

    if selected_system is not None:
        report = inspection.get_system_report(
            GameInstall.discover(summary.root),
            selected_system,
            language=language,
        )
        lines.extend(("", inspection.format_system_report(report)))

    return "\n".join(lines)


def launch_app(
    install_root: str | Path | None = None,
    *,
    selected_system: str | None = None,
    language: str = "english",
) -> str:
    return build_shell_message(
        install_root,
        selected_system=selected_system,
        language=language,
    )
