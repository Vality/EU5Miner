from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

from eu5miner_gui.desktop.bootstrap import DesktopLaunchOptions, launch_desktop_app
from eu5miner_gui.desktop.controller import DesktopController
from eu5miner_gui.desktop.navigation import NavigationTarget

from .desktop_test_support import FakeInspection, diplomacy_helper_view, religion_helper_view


def test_launch_desktop_app_initializes_controller_and_runs_app(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_inspection = FakeInspection(tmp_path / "install")
    controller = DesktopController(
        inspection_module=fake_inspection,
        discover_install=fake_inspection.discover,
        diplomacy_helper_builder=lambda *_args: diplomacy_helper_view(),
        religion_helper_builder=lambda *_args: religion_helper_view(),
    )
    run_calls: list[str] = []

    class FakeApp:
        title = ""

        def build(self):
            return SimpleNamespace(name="root")

        def run(self) -> None:
            run_calls.append("run")
            self.build()

    monkeypatch.setitem(sys.modules, "kivy.app", ModuleType("kivy.app"))
    sys.modules["kivy.app"].App = FakeApp
    monkeypatch.setitem(sys.modules, "kivy.core.window", ModuleType("kivy.core.window"))
    sys.modules["kivy.core.window"].Window = SimpleNamespace(minimum_width=0, minimum_height=0)

    for module_name, attribute_name, value in (
        (
            "eu5miner_gui.desktop.widgets.source_bar",
            "SourceBar",
            lambda **_kwargs: SimpleNamespace(bind_page_host=lambda *_args: None),
        ),
        (
            "eu5miner_gui.desktop.widgets.sidebar",
            "Sidebar",
            lambda **_kwargs: SimpleNamespace(
                bind_page_host=lambda *_args: None,
                refresh=lambda: None,
            ),
        ),
        (
            "eu5miner_gui.desktop.widgets.page_host",
            "PageHost",
            lambda **_kwargs: SimpleNamespace(refresh=lambda: None),
        ),
    ):
        module = ModuleType(module_name)
        setattr(module, attribute_name, value)
        monkeypatch.setitem(sys.modules, module_name, module)

    monkeypatch.setitem(sys.modules, "kivy.uix.boxlayout", ModuleType("kivy.uix.boxlayout"))
    sys.modules["kivy.uix.boxlayout"].BoxLayout = type(
        "FakeBoxLayout",
        (),
        {
            "__init__": lambda self, **_kwargs: setattr(self, "children", []),
            "add_widget": lambda self, widget: self.children.append(widget),
        },
    )

    exit_code = launch_desktop_app(
        controller=controller,
        options=DesktopLaunchOptions(
            install_root=tmp_path / "install",
            initial_target=NavigationTarget.report("map"),
        ),
    )

    assert exit_code == 0
    assert run_calls == ["run"]
    assert controller.navigation_state.current_target == NavigationTarget.report("map")
