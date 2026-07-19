from __future__ import annotations

from pathlib import Path

from eu5miner.gui.desktop.controller import DesktopController
from eu5miner.gui.desktop.navigation import NavigationTarget

from .desktop_test_support import FakeInspection, diplomacy_helper_view, religion_helper_view


def _controller(tmp_path: Path) -> DesktopController:
    fake_inspection = FakeInspection(tmp_path / "install")
    controller = DesktopController(
        inspection_module=fake_inspection,
        discover_install=fake_inspection.discover,
        diplomacy_helper_builder=lambda *_args: diplomacy_helper_view(),
        religion_helper_builder=lambda *_args: religion_helper_view(),
    )
    controller.initialize()
    return controller


def test_sidebar_sections_follow_core_order_plus_explicit_helpers(tmp_path: Path) -> None:
    controller = _controller(tmp_path)

    sections = controller.sidebar_sections()

    assert tuple(section.title for section in sections) == (
        "Overview",
        "Systems",
        "Entities",
        "Helpers",
    )
    assert tuple(item.title for item in sections[1].items) == ("economy", "religion", "map")
    assert tuple(item.title for item in sections[2].items) == ("economy", "religion")
    assert tuple(item.title for item in sections[3].items) == (
        "war-flow",
        "diplomacy-graph",
        "religion-overview",
    )


def test_report_page_exposes_related_entity_list_target(tmp_path: Path) -> None:
    controller = _controller(tmp_path)

    controller.navigate(NavigationTarget.report("economy"))
    page = controller.current_page()

    assert page.kind == "report"
    assert page.primary_link == NavigationTarget.entity_list("economy")


def test_entity_detail_references_expose_clickable_targets(tmp_path: Path) -> None:
    controller = _controller(tmp_path)

    controller.navigate(NavigationTarget.entity_detail("religion", "faith_01"))
    page = controller.current_page()

    assert page.kind == "entity_browser"
    assert page.detail is not None
    references = page.detail.sections[2].items
    assert references[0].target == NavigationTarget.entity_detail("economy", "iron")


def test_helper_page_keeps_mod_scope_notice_explicit(tmp_path: Path) -> None:
    mod_root = tmp_path / "mods" / "sample_mod"
    mod_root.mkdir(parents=True)
    controller = _controller(tmp_path)
    controller.add_mod_folder(mod_root)

    controller.navigate(NavigationTarget.helper("war-flow"))
    page = controller.current_page()

    assert page.kind == "helper"
    assert page.notice is not None
    assert "representative install files only" in page.notice
