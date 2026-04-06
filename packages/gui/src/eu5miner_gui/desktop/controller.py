from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import eu5miner.inspection as inspection
from eu5miner import GameInstall

from eu5miner_gui.desktop.adapters import (
    EntityBrowserPageViewModel,
    EntitySearchRecord,
    TextPageViewModel,
    build_entity_browser_page_view_model,
    build_entity_detail_page_view_model,
    build_entity_search_records,
    build_helper_page_view_model,
    build_overview_page_view_model,
    build_report_page_view_model,
    filter_and_sort_entity_records,
)
from eu5miner_gui.desktop.navigation import NavigationTarget, SidebarItem, SidebarSection
from eu5miner_gui.desktop.state import (
    EntityBrowserUiState,
    EntitySortMode,
    NavigationState,
    PageCacheState,
    SourceSessionState,
    UiState,
)
from eu5miner_gui.diplomacy_helpers import (
    DiplomacyHelperInfo,
    build_diplomacy_helper_view,
    list_diplomacy_helpers,
)
from eu5miner_gui.religion_helpers import (
    ReligionHelperInfo,
    build_religion_helper_view,
    list_religion_helpers,
)


class DesktopController:
    def __init__(
        self,
        *,
        inspection_module: Any = inspection,
        discover_install: Any = GameInstall.discover,
        diplomacy_helper_builder: Any = build_diplomacy_helper_view,
        religion_helper_builder: Any = build_religion_helper_view,
    ) -> None:
        self._inspection = inspection_module
        self._discover_install = discover_install
        self._build_diplomacy_helper_view = diplomacy_helper_builder
        self._build_religion_helper_view = religion_helper_builder
        self.supported_systems: tuple[inspection.SystemInfo, ...] = (
            self._inspection.list_supported_systems()
        )
        self.entity_systems: tuple[inspection.EntitySystemInfo, ...] = (
            self._inspection.list_entity_systems()
        )
        self.diplomacy_helpers: tuple[DiplomacyHelperInfo, ...] = list_diplomacy_helpers()
        self.religion_helpers: tuple[ReligionHelperInfo, ...] = list_religion_helpers()
        self.source_state = SourceSessionState()
        self.navigation_state = NavigationState()
        self.ui_state = UiState()
        self.cache_state = PageCacheState()
        self._active_install: GameInstall | None = None
        self._entity_search_records: dict[str, tuple[EntitySearchRecord, ...]] = {}
        self._report_errors: dict[str, str] = {}
        self._entity_errors: dict[str, str] = {}
        self._detail_errors: dict[tuple[str, str], str] = {}
        self._diplomacy_helper_errors: dict[str, str] = {}
        self._religion_helper_errors: dict[str, str] = {}

    def initialize(
        self,
        *,
        initial_target: NavigationTarget | None = None,
        install_root: str | Path | None = None,
        mod_folders: tuple[str | Path, ...] = (),
    ) -> None:
        self.navigation_state = NavigationState(
            current_target=initial_target or NavigationTarget.overview()
        )
        if install_root is not None:
            self.set_manual_install_root(install_root, navigate=False)
        else:
            self._attempt_auto_discovery()
        for mod_folder in mod_folders:
            self.add_mod_folder(mod_folder, navigate=False)
        if self.navigation_state.current_target.requires_install and self._active_install is None:
            self.navigation_state = NavigationState(current_target=NavigationTarget.overview())

    @property
    def active_install_root(self) -> Path | None:
        return self.source_state.active_install_root

    @property
    def active_mod_folders(self) -> tuple[Path, ...]:
        return self.source_state.extra_mod_folders

    def sidebar_sections(self) -> tuple[SidebarSection, ...]:
        helper_items = tuple(
            [
                SidebarItem(
                    title=helper.name,
                    subtitle=helper.description,
                    target=NavigationTarget.helper(helper.name),
                )
                for helper in self.diplomacy_helpers
            ]
            + [
                SidebarItem(
                    title=helper.name,
                    subtitle=helper.description,
                    target=NavigationTarget.helper(helper.name),
                )
                for helper in self.religion_helpers
            ]
        )
        return (
            SidebarSection(
                title="Overview",
                items=(
                    SidebarItem(
                        title="overview",
                        subtitle="Install, source, and coverage summary.",
                        target=NavigationTarget.overview(),
                    ),
                ),
            ),
            SidebarSection(
                title="Systems",
                items=tuple(
                    SidebarItem(
                        title=info.name,
                        subtitle=info.description,
                        target=NavigationTarget.report(info.name),
                    )
                    for info in self.supported_systems
                ),
            ),
            SidebarSection(
                title="Entities",
                items=tuple(
                    SidebarItem(
                        title=info.name,
                        subtitle=info.description,
                        target=NavigationTarget.entity_list(info.name),
                    )
                    for info in self.entity_systems
                ),
            ),
            SidebarSection(title="Helpers", items=helper_items),
        )

    def navigate(self, target: NavigationTarget) -> None:
        if target.requires_install and self._active_install is None:
            self.navigation_state = NavigationState(
                current_target=NavigationTarget.overview()
            )
            self.source_state = replace(
                self.source_state,
                load_status="error",
                error_message="Select an install root before opening install-backed pages.",
            )
            return
        if target.kind == "entity_list":
            self._ensure_entity_browser_state(target.system or "")
        if (
            target.kind == "entity_detail"
            and target.system is not None
            and target.entity_name is not None
        ):
            self._set_selected_entity(target.system, target.entity_name)
        self.navigation_state = NavigationState(current_target=target)

    def reload(self) -> None:
        if self.source_state.manual_install_root is not None:
            self.set_manual_install_root(self.source_state.manual_install_root, navigate=False)
            return
        self._attempt_auto_discovery()

    def set_manual_install_root(
        self,
        install_root: str | Path | None,
        *,
        navigate: bool = True,
    ) -> None:
        if install_root is None or str(install_root).strip() == "":
            self.source_state = replace(self.source_state, manual_install_root=None)
            self._attempt_auto_discovery()
            if navigate:
                self.navigate(self.navigation_state.current_target)
            return
        normalized_root = Path(install_root).expanduser().resolve()
        try:
            install = self._discover_install(normalized_root)
        except (FileNotFoundError, ValueError) as exc:
            self.source_state = replace(
                self.source_state,
                manual_install_root=normalized_root,
                active_install_root=None,
                source_summary=None,
                load_status="error",
                error_message=str(exc),
            )
            self._active_install = None
            self._invalidate_cache()
            return
        self._apply_install(install, manual_root=normalized_root)
        if navigate:
            self.navigate(self.navigation_state.current_target)

    def add_mod_folder(self, mod_folder: str | Path, *, navigate: bool = True) -> None:
        normalized_mod_folder = Path(mod_folder).expanduser().resolve()
        if not normalized_mod_folder.exists() or not normalized_mod_folder.is_dir():
            self.source_state = replace(
                self.source_state,
                load_status="error",
                error_message=f"Mod folder '{normalized_mod_folder}' does not exist.",
            )
            return
        if normalized_mod_folder in self.source_state.extra_mod_folders:
            self.ui_state = replace(
                self.ui_state,
                selected_mod_folder=normalized_mod_folder,
            )
            return
        mod_folders = self.source_state.extra_mod_folders + (normalized_mod_folder,)
        self.source_state = replace(self.source_state, extra_mod_folders=mod_folders)
        self.ui_state = replace(self.ui_state, selected_mod_folder=normalized_mod_folder)
        self._refresh_summary()
        if navigate:
            self.navigate(self.navigation_state.current_target)

    def remove_selected_mod_folder(self) -> None:
        selected_mod_folder = self.ui_state.selected_mod_folder
        if selected_mod_folder is None:
            return
        self.remove_mod_folder(selected_mod_folder)

    def remove_mod_folder(self, mod_folder: str | Path) -> None:
        normalized_mod_folder = Path(mod_folder).expanduser().resolve()
        remaining_mod_folders = tuple(
            candidate
            for candidate in self.source_state.extra_mod_folders
            if candidate != normalized_mod_folder
        )
        next_selected_mod_folder = remaining_mod_folders[-1] if remaining_mod_folders else None
        self.source_state = replace(
            self.source_state,
            extra_mod_folders=remaining_mod_folders,
        )
        self.ui_state = replace(self.ui_state, selected_mod_folder=next_selected_mod_folder)
        self._refresh_summary()
        self.navigate(self.navigation_state.current_target)

    def select_mod_folder(self, mod_folder: str | Path | None) -> None:
        if mod_folder is None:
            self.ui_state = replace(self.ui_state, selected_mod_folder=None)
            return
        self.ui_state = replace(
            self.ui_state,
            selected_mod_folder=Path(mod_folder).expanduser().resolve(),
        )

    def set_entity_search_text(self, system: str, search_text: str) -> None:
        ui_state = self._ensure_entity_browser_state(system)
        self.ui_state.entity_browsers[system] = replace(ui_state, search_text=search_text)
        if (
            self.navigation_state.current_target.kind == "entity_detail"
            and self.navigation_state.current_target.system == system
        ):
            self.navigation_state = NavigationState(
                current_target=NavigationTarget.entity_list(system)
            )

    def set_entity_sort_mode(self, system: str, sort_mode: str) -> None:
        if sort_mode not in {"name", "group", "source"}:
            raise ValueError("Entity sort mode must be one of: group, name, source.")
        ui_state = self._ensure_entity_browser_state(system)
        self.ui_state.entity_browsers[system] = replace(
            ui_state,
            sort_mode=cast(EntitySortMode, sort_mode),
        )

    def set_selected_entity(self, system: str, entity_name: str) -> None:
        self._set_selected_entity(system, entity_name)
        self.navigation_state = NavigationState(
            current_target=NavigationTarget.entity_detail(system, entity_name)
        )

    def current_page(self) -> TextPageViewModel | EntityBrowserPageViewModel:
        target = self.navigation_state.current_target
        if target.kind == "overview":
            return build_overview_page_view_model(
                summary=self.source_state.source_summary,
                supported_systems=self.supported_systems,
                entity_systems=self.entity_systems,
                diplomacy_helpers=self.diplomacy_helpers,
                religion_helpers=self.religion_helpers,
                status=(
                    "ready"
                    if self.source_state.source_summary is not None
                    else self.source_state.load_status
                ),
                notice=self._overview_notice(),
            )
        if target.kind == "report":
            assert target.system is not None
            return self._build_report_page(target.system)
        if target.kind == "entity_list":
            assert target.system is not None
            return self._build_entity_browser_page(target.system)
        if target.kind == "entity_detail":
            assert target.system is not None
            assert target.entity_name is not None
            self._set_selected_entity(target.system, target.entity_name)
            return self._build_entity_browser_page(target.system)
        assert target.helper_name is not None
        return self._build_helper_page(target.helper_name)

    def _attempt_auto_discovery(self) -> None:
        try:
            install = self._discover_install(None)
        except (FileNotFoundError, ValueError) as exc:
            self._active_install = None
            self.source_state = replace(
                self.source_state,
                discovered_install_root=None,
                active_install_root=None,
                source_summary=None,
                load_status="error",
                error_message=str(exc),
            )
            self._invalidate_cache()
            return
        self._apply_install(install, manual_root=self.source_state.manual_install_root)
        self.source_state = replace(
            self.source_state,
            discovered_install_root=install.root,
        )

    def _apply_install(self, install: GameInstall, *, manual_root: Path | None) -> None:
        self._active_install = install
        self.source_state = replace(
            self.source_state,
            manual_install_root=manual_root,
            active_install_root=install.root,
            load_status="loading",
            error_message=None,
        )
        self._refresh_summary()

    def _refresh_summary(self) -> None:
        generation = self.source_state.reload_generation + 1
        self._invalidate_cache(generation=generation)
        if self._active_install is None:
            self.source_state = replace(
                self.source_state,
                source_summary=None,
                load_status="error",
            )
            return
        try:
            summary = self._inspection.summarize_install(
                self._active_install,
                mod_roots=self.source_state.extra_mod_folders,
            )
        except (FileNotFoundError, ValueError) as exc:
            self.source_state = replace(
                self.source_state,
                source_summary=None,
                load_status="error",
                error_message=str(exc),
                reload_generation=generation,
            )
            return
        self.source_state = replace(
            self.source_state,
            source_summary=summary,
            active_install_root=self._active_install.root,
            load_status="ready",
            error_message=None,
            reload_generation=generation,
        )

    def _invalidate_cache(self, *, generation: int | None = None) -> None:
        next_generation = (
            generation
            if generation is not None
            else self.source_state.reload_generation + 1
        )
        self.cache_state.reset(next_generation)
        self._entity_search_records.clear()
        self._report_errors.clear()
        self._entity_errors.clear()
        self._detail_errors.clear()
        self._diplomacy_helper_errors.clear()
        self._religion_helper_errors.clear()

    def _build_report_page(self, system: str) -> TextPageViewModel:
        info = self._supported_system_info(system)
        if self._active_install is None:
            return build_report_page_view_model(
                info=info,
                report=None,
                reason="Reports require a discovered or selected install root.",
                entity_target=self._entity_list_target(system),
            )
        report = self.cache_state.reports.get(system)
        if report is None and system not in self._report_errors:
            try:
                report = self._inspection.get_system_report(self._active_install, system)
            except (FileNotFoundError, KeyError, ValueError) as exc:
                self._report_errors[system] = str(exc)
            else:
                self.cache_state.reports[system] = report
        return build_report_page_view_model(
            info=info,
            report=self.cache_state.reports.get(system),
            reason=self._report_errors.get(system),
            entity_target=self._entity_list_target(system),
        )

    def _build_entity_browser_page(self, system: str) -> EntityBrowserPageViewModel:
        info = self._entity_system_info(system)
        browser_state = self._ensure_entity_browser_state(system)
        if self._active_install is None:
            return build_entity_browser_page_view_model(
                info=info,
                records=(),
                total_count=0,
                search_text=browser_state.search_text,
                sort_mode=browser_state.sort_mode,
                detail=None,
                selected_entity_name=None,
                reason="Entity browsing requires a discovered or selected install root.",
            )
        all_records, reason = self._entity_records_for(system)
        if reason is not None:
            return build_entity_browser_page_view_model(
                info=info,
                records=(),
                total_count=0,
                search_text=browser_state.search_text,
                sort_mode=browser_state.sort_mode,
                detail=None,
                selected_entity_name=None,
                reason=reason,
            )
        filtered_records = filter_and_sort_entity_records(
            all_records,
            search_text=browser_state.search_text,
            sort_mode=browser_state.sort_mode,
        )
        selected_entity_name = browser_state.selected_entity_name
        visible_names = {record.summary.name for record in filtered_records}
        if selected_entity_name not in visible_names:
            selected_entity_name = (
                filtered_records[0].summary.name if filtered_records else None
            )
            self.ui_state.entity_browsers[system] = replace(
                browser_state,
                selected_entity_name=selected_entity_name,
            )
        detail_view_model = None
        if selected_entity_name is not None:
            detail_view_model = self._build_entity_detail_page(system, selected_entity_name)
        return build_entity_browser_page_view_model(
            info=info,
            records=filtered_records,
            total_count=len(all_records),
            search_text=browser_state.search_text,
            sort_mode=browser_state.sort_mode,
            detail=detail_view_model,
            selected_entity_name=selected_entity_name,
            reason=None,
        )

    def _build_entity_detail_page(self, system: str, entity_name: str) -> TextPageViewModel:
        info = self._entity_system_info(system)
        if self._active_install is None:
            return build_entity_detail_page_view_model(
                info=info,
                detail=None,
                reason="Entity detail requires a discovered or selected install root.",
                browsable_systems=self._browsable_system_names(),
            )
        cache_key = (system, entity_name)
        detail = self.cache_state.entity_details.get(cache_key)
        if detail is None and cache_key not in self._detail_errors:
            try:
                detail = self._inspection.get_system_entity(
                    self._active_install,
                    system,
                    entity_name,
                    mod_roots=self.source_state.extra_mod_folders,
                )
            except (FileNotFoundError, KeyError, ValueError) as exc:
                self._detail_errors[cache_key] = str(exc)
            else:
                self.cache_state.entity_details[cache_key] = detail
        return build_entity_detail_page_view_model(
            info=info,
            detail=self.cache_state.entity_details.get(cache_key),
            reason=self._detail_errors.get(cache_key),
            browsable_systems=self._browsable_system_names(),
        )

    def _build_helper_page(self, helper_name: str) -> TextPageViewModel:
        if self._active_install is None:
            return build_helper_page_view_model(
                info=self._helper_info(helper_name),
                view=None,
                reason="Helper pages require a discovered or selected install root.",
                notice=self._helper_notice(),
            )
        if self._is_diplomacy_helper(helper_name):
            helper_info = self._diplomacy_helper_info(helper_name)
            diplomacy_view = self.cache_state.diplomacy_helpers.get(helper_name)
            if (
                diplomacy_view is None
                and helper_name not in self._diplomacy_helper_errors
            ):
                try:
                    diplomacy_view = self._build_diplomacy_helper_view(
                        self._active_install,
                        helper_name,
                    )
                except (FileNotFoundError, KeyError, ValueError) as exc:
                    self._diplomacy_helper_errors[helper_name] = str(exc)
                else:
                    self.cache_state.diplomacy_helpers[helper_name] = diplomacy_view
            return build_helper_page_view_model(
                info=helper_info,
                view=self.cache_state.diplomacy_helpers.get(helper_name),
                reason=self._diplomacy_helper_errors.get(helper_name),
                notice=self._helper_notice(),
            )
        religion_helper_info = self._religion_helper_info(helper_name)
        religion_view = self.cache_state.religion_helpers.get(helper_name)
        if religion_view is None and helper_name not in self._religion_helper_errors:
            try:
                religion_view = self._build_religion_helper_view(
                    self._active_install,
                    helper_name,
                )
            except (FileNotFoundError, KeyError, ValueError) as exc:
                self._religion_helper_errors[helper_name] = str(exc)
            else:
                self.cache_state.religion_helpers[helper_name] = religion_view
        return build_helper_page_view_model(
            info=religion_helper_info,
            view=self.cache_state.religion_helpers.get(helper_name),
            reason=self._religion_helper_errors.get(helper_name),
            notice=self._helper_notice(),
        )

    def _entity_records_for(
        self,
        system: str,
    ) -> tuple[tuple[EntitySearchRecord, ...], str | None]:
        records = self._entity_search_records.get(system)
        if records is not None:
            return records, None
        if self._active_install is None:
            return (), "Entity browsing requires a discovered or selected install root."
        try:
            summaries = self._inspection.list_system_entities(
                self._active_install,
                system,
                mod_roots=self.source_state.extra_mod_folders,
            )
        except (FileNotFoundError, KeyError, ValueError) as exc:
            self._entity_errors[system] = str(exc)
            return (), str(exc)
        self.cache_state.entity_summaries[system] = summaries
        records = build_entity_search_records(summaries)
        self._entity_search_records[system] = records
        return records, None

    def _ensure_entity_browser_state(self, system: str) -> EntityBrowserUiState:
        ui_state = self.ui_state.entity_browsers.get(system)
        if ui_state is None:
            ui_state = EntityBrowserUiState()
            self.ui_state.entity_browsers[system] = ui_state
        return ui_state

    def _set_selected_entity(self, system: str, entity_name: str) -> None:
        ui_state = self._ensure_entity_browser_state(system)
        self.ui_state.entity_browsers[system] = replace(
            ui_state,
            selected_entity_name=entity_name,
        )

    def _supported_system_info(self, system: str) -> inspection.SystemInfo:
        for info in self.supported_systems:
            if info.name == system:
                return info
        raise KeyError(system)

    def _entity_system_info(self, system: str) -> inspection.EntitySystemInfo:
        for info in self.entity_systems:
            if info.name == system:
                return info
        raise KeyError(system)

    def _entity_list_target(self, system: str) -> NavigationTarget | None:
        if system in self._browsable_system_names():
            return NavigationTarget.entity_list(system)
        return None

    def _browsable_system_names(self) -> set[str]:
        return {info.name for info in self.entity_systems}

    def _helper_info(self, helper_name: str) -> DiplomacyHelperInfo | ReligionHelperInfo:
        helper_info = next(
            (helper for helper in self.diplomacy_helpers if helper.name == helper_name),
            None,
        )
        if helper_info is not None:
            return helper_info
        religion_helper_info = next(
            (helper for helper in self.religion_helpers if helper.name == helper_name),
            None,
        )
        if religion_helper_info is not None:
            return religion_helper_info
        raise KeyError(helper_name)

    def _diplomacy_helper_info(self, helper_name: str) -> DiplomacyHelperInfo:
        for helper in self.diplomacy_helpers:
            if helper.name == helper_name:
                return helper
        raise KeyError(helper_name)

    def _religion_helper_info(self, helper_name: str) -> ReligionHelperInfo:
        for helper in self.religion_helpers:
            if helper.name == helper_name:
                return helper
        raise KeyError(helper_name)

    def _is_diplomacy_helper(self, helper_name: str) -> bool:
        return any(helper.name == helper_name for helper in self.diplomacy_helpers)

    def _overview_notice(self) -> str | None:
        if self.source_state.load_status == "error":
            return self.source_state.error_message
        if self.source_state.source_summary is None:
            return "Auto-discovery is ready, but no install has been loaded yet."
        if self.source_state.extra_mod_folders:
            mod_list = ", ".join(str(path) for path in self.source_state.extra_mod_folders)
            return f"Active extra mod folders: {mod_list}"
        return None

    def _helper_notice(self) -> str | None:
        if self.source_state.extra_mod_folders:
            return (
                "Helper pages use representative install files only; extra mod folders do not "
                "currently change helper coverage."
            )
        return None
