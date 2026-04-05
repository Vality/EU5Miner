"""Curated stable root exports for install discovery, VFS access, and mod workflows.

Import read-only install summaries from ``eu5miner.inspection`` and concept-local
helpers from grouped packages under ``eu5miner.domains``.
"""

from eu5miner.mods import (
    AppliedModUpdate,
    AppliedModWrite,
    BlockedModEmission,
    ModUpdateAdvisory,
    ModUpdateAdvisoryKind,
    ModUpdateWarning,
    ModUpdateWarningKind,
    ModUpdateWrite,
    ModUpdateWriteKind,
    PlannedModUpdate,
    apply_mod_update,
    format_mod_update_report,
    plan_mod_update,
)
from eu5miner.paths import DEFAULT_WINDOWS_INSTALL, resolve_install_path
from eu5miner.source import ContentPhase, GameInstall
from eu5miner.vfs import ContentSource, SourceKind, VirtualFilesystem

__all__ = [
    "AppliedModUpdate",
    "AppliedModWrite",
    "BlockedModEmission",
    "ContentPhase",
    "ContentSource",
    "DEFAULT_WINDOWS_INSTALL",
    "GameInstall",
    "ModUpdateAdvisory",
    "ModUpdateAdvisoryKind",
    "ModUpdateWarning",
    "ModUpdateWarningKind",
    "ModUpdateWrite",
    "ModUpdateWriteKind",
    "PlannedModUpdate",
    "SourceKind",
    "VirtualFilesystem",
    "apply_mod_update",
    "format_mod_update_report",
    "plan_mod_update",
    "resolve_install_path",
]
