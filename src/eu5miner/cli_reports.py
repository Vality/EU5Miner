"""Backward-compatible wrapper for CLI-facing report helpers."""

from __future__ import annotations

from eu5miner.inspection import (
    SystemInfo as CliSystemInfo,
)
from eu5miner.inspection import (
    SystemReport as CliSystemReport,
)
from eu5miner.inspection import (
    format_system_report,
)
from eu5miner.inspection import (
    get_system_report as build_system_report,
)
from eu5miner.inspection import (
    list_supported_systems as list_systems,
)

__all__ = [
    "CliSystemInfo",
    "CliSystemReport",
    "build_system_report",
    "format_system_report",
    "list_systems",
]
