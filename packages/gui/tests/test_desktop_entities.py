from __future__ import annotations

from pathlib import Path

from eu5miner_gui.desktop.controller import DesktopController
from eu5miner_gui.desktop.navigation import NavigationTarget

from .desktop_test_support import FakeInspection, diplomacy_helper_view, religion_helper_view


def _controller(tmp_path: Path) -> tuple[DesktopController, FakeInspection]:
    fake_inspection = FakeInspection(tmp_path / "install")
    controller = DesktopController(
        inspection_module=fake_inspection,
        discover_install=fake_inspection.discover,
        diplomacy_helper_builder=lambda *_args: diplomacy_helper_view(),
        religion_helper_builder=lambda *_args: religion_helper_view(),
    )
    controller.initialize()
    return controller, fake_inspection


def test_entity_browser_filters_large_lists_and_sorts_by_group(tmp_path: Path) -> None:
    controller, _ = _controller(tmp_path)

    controller.navigate(NavigationTarget.entity_list("religion"))
    controller.set_entity_search_text("religion", "faith_10")
    controller.set_entity_sort_mode("religion", "group")
    page = controller.current_page()

    assert page.kind == "entity_browser"
    assert page.visible_count == 1
    assert page.rows[0].name == "faith_10"
    assert page.selected_entity_name == "faith_10"


def test_entity_browser_uses_lazy_detail_loading(tmp_path: Path) -> None:
    controller, fake_inspection = _controller(tmp_path)

    controller.navigate(NavigationTarget.entity_list("religion"))
    page = controller.current_page()

    assert page.kind == "entity_browser"
    assert fake_inspection.detail_calls == [("religion", "faith_01")]

    controller.navigate(NavigationTarget.entity_detail("religion", "faith_03"))
    page = controller.current_page()

    assert page.kind == "entity_browser"
    assert fake_inspection.detail_calls[-1] == ("religion", "faith_03")


def test_entity_browser_reference_target_switches_detail_system(tmp_path: Path) -> None:
    controller, _ = _controller(tmp_path)

    controller.navigate(NavigationTarget.entity_detail("religion", "faith_02"))
    page = controller.current_page()
    target = page.detail.sections[2].items[0].target

    assert target == NavigationTarget.entity_detail("economy", "iron")
    controller.navigate(target)
    next_page = controller.current_page()
    assert next_page.kind == "entity_browser"
    assert next_page.selected_entity_name == "iron"
