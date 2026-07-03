from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import eu5miner.inspection as inspection

from eu5miner_gui.desktop.navigation import NavigationTarget
from eu5miner_gui.diplomacy_helpers import DiplomacyHelperView
from eu5miner_gui.religion_helpers import ReligionHelperView

LoadStatus = Literal["idle", "loading", "ready", "error"]
EntitySortMode = Literal["name", "group", "source"]


@dataclass(frozen=True)
class SourceSessionState:
    discovered_install_root: Path | None = None
    manual_install_root: Path | None = None
    active_install_root: Path | None = None
    extra_mod_folders: tuple[Path, ...] = ()
    source_summary: inspection.InstallSummary | None = None
    reload_generation: int = 0
    load_status: LoadStatus = "idle"
    error_message: str | None = None


@dataclass(frozen=True)
class NavigationState:
    current_target: NavigationTarget = field(default_factory=NavigationTarget.overview)


@dataclass(frozen=True)
class EntityBrowserUiState:
    search_text: str = ""
    sort_mode: EntitySortMode = "name"
    selected_entity_name: str | None = None


@dataclass(frozen=True)
class UiState:
    entity_browsers: dict[str, EntityBrowserUiState] = field(default_factory=dict)
    selected_mod_folder: Path | None = None


@dataclass
class PageCacheState:
    generation: int = 0
    reports: dict[str, inspection.SystemReport] = field(default_factory=dict)
    entity_summaries: dict[str, tuple[inspection.EntitySummary, ...]] = field(default_factory=dict)
    entity_details: dict[tuple[str, str], inspection.EntityDetail] = field(default_factory=dict)
    diplomacy_helpers: dict[str, DiplomacyHelperView] = field(default_factory=dict)
    religion_helpers: dict[str, ReligionHelperView] = field(default_factory=dict)

    def reset(self, generation: int) -> None:
        self.generation = generation
        self.reports.clear()
        self.entity_summaries.clear()
        self.entity_details.clear()
        self.diplomacy_helpers.clear()
        self.religion_helpers.clear()
