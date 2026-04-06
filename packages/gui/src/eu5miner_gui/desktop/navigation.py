from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from eu5miner_gui.browser import parse_browser_page_selection

NavigationTargetKind = Literal[
    "overview",
    "report",
    "entity_list",
    "entity_detail",
    "helper",
]


@dataclass(frozen=True)
class NavigationTarget:
    kind: NavigationTargetKind
    system: str | None = None
    entity_name: str | None = None
    helper_name: str | None = None

    @property
    def page_key(self) -> str:
        if self.kind == "overview":
            return "overview"
        if self.kind == "report":
            assert self.system is not None
            return f"report:{self.system}"
        if self.kind == "entity_list":
            assert self.system is not None
            return f"entities:{self.system}"
        if self.kind == "entity_detail":
            assert self.system is not None
            assert self.entity_name is not None
            return f"entity:{self.system}:{self.entity_name}"
        assert self.helper_name is not None
        return f"helper:{self.helper_name}"

    @property
    def requires_install(self) -> bool:
        return self.kind != "overview"

    @classmethod
    def overview(cls) -> NavigationTarget:
        return cls(kind="overview")

    @classmethod
    def report(cls, system: str) -> NavigationTarget:
        return cls(kind="report", system=system)

    @classmethod
    def entity_list(cls, system: str) -> NavigationTarget:
        return cls(kind="entity_list", system=system)

    @classmethod
    def entity_detail(cls, system: str, entity_name: str) -> NavigationTarget:
        return cls(kind="entity_detail", system=system, entity_name=entity_name)

    @classmethod
    def helper(cls, helper_name: str) -> NavigationTarget:
        return cls(kind="helper", helper_name=helper_name)


@dataclass(frozen=True)
class SidebarItem:
    title: str
    subtitle: str
    target: NavigationTarget


@dataclass(frozen=True)
class SidebarSection:
    title: str
    items: tuple[SidebarItem, ...]


def navigation_target_from_page_key(page_key: str) -> NavigationTarget:
    selection = parse_browser_page_selection(page_key)
    if selection.selected_system is not None:
        return NavigationTarget.report(selection.selected_system)
    if selection.selected_entity_system is not None and selection.selected_entity_name is None:
        return NavigationTarget.entity_list(selection.selected_entity_system)
    if selection.selected_entity_system is not None and selection.selected_entity_name is not None:
        return NavigationTarget.entity_detail(
            selection.selected_entity_system,
            selection.selected_entity_name,
        )
    if selection.selected_religion_helper is not None:
        return NavigationTarget.helper(selection.selected_religion_helper)
    if selection.selected_diplomacy_helper is not None:
        return NavigationTarget.helper(selection.selected_diplomacy_helper)
    return NavigationTarget.overview()
