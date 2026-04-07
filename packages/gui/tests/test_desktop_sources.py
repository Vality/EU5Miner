from __future__ import annotations

from pathlib import Path

from eu5miner_gui.desktop.controller import DesktopController
from eu5miner_gui.desktop.navigation import NavigationTarget

from .desktop_test_support import FakeInspection, diplomacy_helper_view, religion_helper_view


def test_controller_auto_discovery_success_loads_overview(tmp_path: Path) -> None:
    fake_inspection = FakeInspection(tmp_path / "install")
    controller = DesktopController(
        inspection_module=fake_inspection,
        discover_install=fake_inspection.discover,
        diplomacy_helper_builder=lambda *_args: diplomacy_helper_view(),
        religion_helper_builder=lambda *_args: religion_helper_view(),
    )

    controller.initialize()

    page = controller.current_page()
    assert controller.active_install_root == tmp_path / "install"
    assert controller.source_state.load_status == "ready"
    assert page.kind == "overview"
    assert page.source_layers[0].kind == "vanilla"


def test_controller_auto_discovery_failure_keeps_recoverable_overview(tmp_path: Path) -> None:
    fake_inspection = FakeInspection(
        tmp_path / "install",
        auto_discover_error=FileNotFoundError("No install was discovered."),
    )
    controller = DesktopController(
        inspection_module=fake_inspection,
        discover_install=fake_inspection.discover,
        diplomacy_helper_builder=lambda *_args: diplomacy_helper_view(),
        religion_helper_builder=lambda *_args: religion_helper_view(),
    )

    controller.initialize(initial_target=NavigationTarget.report("map"))

    page = controller.current_page()
    assert controller.active_install_root is None
    assert controller.navigation_state.current_target.kind == "overview"
    assert page.kind == "overview"
    assert page.notice == "No install was discovered."


def test_controller_manual_override_and_mod_folder_reload(tmp_path: Path) -> None:
    install_root = tmp_path / "install"
    install_root.mkdir()
    mod_root = tmp_path / "mods" / "sample_mod"
    mod_root.mkdir(parents=True)
    fake_inspection = FakeInspection(tmp_path / "auto")
    controller = DesktopController(
        inspection_module=fake_inspection,
        discover_install=fake_inspection.discover,
        diplomacy_helper_builder=lambda *_args: diplomacy_helper_view(),
        religion_helper_builder=lambda *_args: religion_helper_view(),
    )

    controller.initialize()
    initial_generation = controller.source_state.reload_generation
    controller.set_manual_install_root(install_root)
    controller.add_mod_folder(mod_root)

    assert controller.active_install_root == install_root
    assert controller.active_mod_folders == (mod_root.resolve(),)
    assert controller.source_state.reload_generation > initial_generation
    assert fake_inspection.summarize_calls[-1] == (install_root.resolve(), (mod_root.resolve(),))

    controller.remove_selected_mod_folder()

    assert controller.active_mod_folders == ()
    assert fake_inspection.summarize_calls[-1] == (install_root.resolve(), ())


def test_controller_reload_recovers_to_overview_when_auto_discovery_fails(
    tmp_path: Path,
) -> None:
    fake_inspection = FakeInspection(tmp_path / "install")
    controller = DesktopController(
        inspection_module=fake_inspection,
        discover_install=fake_inspection.discover,
        diplomacy_helper_builder=lambda *_args: diplomacy_helper_view(),
        religion_helper_builder=lambda *_args: religion_helper_view(),
    )

    controller.initialize(initial_target=NavigationTarget.report("map"))
    fake_inspection.auto_discover_error = FileNotFoundError("No install was discovered.")

    controller.reload()

    page = controller.current_page()
    assert controller.active_install_root is None
    assert controller.navigation_state.current_target == NavigationTarget.overview()
    assert page.kind == "overview"
    assert page.notice == "No install was discovered."
