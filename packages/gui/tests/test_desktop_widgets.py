from __future__ import annotations

import importlib
import math
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

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


class _FakeWidget:
    def __init__(self, **kwargs) -> None:
        self.children: list[object] = []
        self.parent: object | None = None
        self.width = kwargs.pop("width", 240)
        self.height = kwargs.pop("height", 40)
        self.size_hint = kwargs.pop("size_hint", (1, 1))
        self.size_hint_x = kwargs.pop("size_hint_x", None)
        self.size_hint_y = kwargs.pop("size_hint_y", None)
        self.orientation = kwargs.pop("orientation", "vertical")
        self.spacing = kwargs.pop("spacing", 0)
        self.padding = kwargs.pop("padding", 0)
        self.text = kwargs.pop("text", "")
        self.halign = kwargs.pop("halign", "left")
        self.valign = kwargs.pop("valign", "middle")
        self.markup = kwargs.pop("markup", False)
        self.multiline = kwargs.pop("multiline", False)
        self.hint_text = kwargs.pop("hint_text", "")
        self.values = kwargs.pop("values", ())
        self.bar_width = kwargs.pop("bar_width", 0)
        self.viewclass = kwargs.pop("viewclass", None)
        self.layout_manager = kwargs.pop("layout_manager", None)
        self.callback = kwargs.pop("callback", None)
        self.text_size = kwargs.pop("text_size", (self.width, None))
        self.texture_size = kwargs.pop("texture_size", (0, 16))
        self.minimum_height = kwargs.pop("minimum_height", 0)
        self.disabled = kwargs.pop("disabled", False)
        self.pos = kwargs.pop("pos", (0, 0))
        self.canvas = type(
            "Canvas",
            (),
            {"before": type("Before", (), {"clear": lambda self: None})()},
        )()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_widget(self, widget: Any) -> None:
        widget.parent = self
        self.children.append(widget)

    def clear_widgets(self) -> None:
        for child in self.children:
            child.parent = None
        self.children = []

    def bind(self, **_kwargs):
        return None

    def setter(self, name: str):
        def _set_attr(_: object, value: object) -> None:
            setattr(self, name, value)

        return _set_attr

    def texture_update(self) -> None:
        text = str(self.text or "")
        available_width = self.text_size[0]
        characters_per_line = max(int((available_width or self.width) / 8), 1)
        line_count = 0
        for line in text.splitlines() or [""]:
            line_count += max(1, math.ceil(max(len(line), 1) / characters_per_line))
        self.texture_size = (
            min((available_width or self.width), max(len(text), 1) * 8),
            16 * line_count,
        )


class _FakeBoxLayout(_FakeWidget):
    pass


class _FakeButton(_FakeWidget):
    pass


class _FakeLabel(_FakeWidget):
    pass


class _FakeTextInput(_FakeWidget):
    pass


class _FakeSpinner(_FakeWidget):
    pass


class _FakeScrollView(_FakeWidget):
    pass


class _FakeAccordion(_FakeWidget):
    pass


class _FakeAccordionItem(_FakeWidget):
    pass


class _FakeRecycleView(_FakeWidget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data: list[dict[str, object]] = []


class _FakeRecycleBoxLayout(_FakeBoxLayout):
    pass


class _FakeRecycleDataViewBehavior:
    pass


class _FakeClockEvent:
    def cancel(self) -> None:
        return None


class _FakeFactory:
    @staticmethod
    def register(*_args, **_kwargs) -> None:
        return None


def _fake_schedule_once(_callback, _delay: float) -> _FakeClockEvent:
    return _FakeClockEvent()


def _install_fake_kivy(monkeypatch: pytest.MonkeyPatch) -> None:
    module_map = {
        "kivy.clock": {
            "Clock": type(
                "Clock",
                (),
                {"schedule_once": staticmethod(_fake_schedule_once)},
            )
        },
        "kivy.factory": {"Factory": _FakeFactory},
        "kivy.properties": {
            "BooleanProperty": lambda default=False, **_kwargs: default,
            "NumericProperty": lambda default=0, **_kwargs: default,
            "ObjectProperty": lambda default=None, **_kwargs: default,
            "StringProperty": lambda default="", **_kwargs: default,
        },
        "kivy.uix.boxlayout": {"BoxLayout": _FakeBoxLayout},
        "kivy.uix.button": {"Button": _FakeButton},
        "kivy.uix.label": {"Label": _FakeLabel},
        "kivy.uix.textinput": {"TextInput": _FakeTextInput},
        "kivy.uix.spinner": {"Spinner": _FakeSpinner},
        "kivy.uix.scrollview": {"ScrollView": _FakeScrollView},
        "kivy.uix.accordion": {
            "Accordion": _FakeAccordion,
            "AccordionItem": _FakeAccordionItem,
        },
        "kivy.uix.recycleview": {"RecycleView": _FakeRecycleView},
        "kivy.uix.recycleboxlayout": {"RecycleBoxLayout": _FakeRecycleBoxLayout},
        "kivy.uix.recycleview.views": {
            "RecycleDataViewBehavior": _FakeRecycleDataViewBehavior,
        },
    }
    for module_name, attributes in module_map.items():
        module = ModuleType(module_name)
        for attribute_name, value in attributes.items():
            setattr(module, attribute_name, value)
        monkeypatch.setitem(sys.modules, module_name, module)


def _install_fake_visual_modules(monkeypatch: pytest.MonkeyPatch) -> None:
    visuals = ModuleType("eu5miner_gui.desktop.widgets.visuals")
    visuals.apply_card_background = lambda *_args, **_kwargs: None
    visuals.build_wrapped_button = lambda *args, **kwargs: _FakeButton(*args, **kwargs)
    visuals.build_wrapped_label = lambda *args, **kwargs: _FakeLabel(*args, **kwargs)

    class FakeSourceLayerStrip(_FakeWidget):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

    class FakeStatChipRow(_FakeWidget):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

    visuals.SourceLayerStrip = FakeSourceLayerStrip
    visuals.StatChipRow = FakeStatChipRow
    monkeypatch.setitem(sys.modules, "eu5miner_gui.desktop.widgets.visuals", visuals)


def _load_page_host_stack(monkeypatch: pytest.MonkeyPatch):
    _install_fake_kivy(monkeypatch)
    _install_fake_visual_modules(monkeypatch)

    overview_module = ModuleType("eu5miner_gui.desktop.widgets.overview_page")

    class FakeOverviewPageWidget(_FakeWidget):
        def __init__(self, page, navigate, **kwargs) -> None:
            super().__init__(page=page, navigate=navigate, **kwargs)

    overview_module.OverviewPageWidget = FakeOverviewPageWidget
    monkeypatch.setitem(sys.modules, "eu5miner_gui.desktop.widgets.overview_page", overview_module)

    report_module = ModuleType("eu5miner_gui.desktop.widgets.report_page")

    class FakeReportPageWidget(_FakeWidget):
        def __init__(self, page, navigate, **kwargs) -> None:
            super().__init__(page=page, navigate=navigate, **kwargs)

    class FakeHelperPageWidget(FakeReportPageWidget):
        pass

    report_module.ReportPageWidget = FakeReportPageWidget
    report_module.HelperPageWidget = FakeHelperPageWidget
    monkeypatch.setitem(sys.modules, "eu5miner_gui.desktop.widgets.report_page", report_module)

    entity_module = ModuleType("eu5miner_gui.desktop.widgets.entity_browser_page")

    class FakeEntityBrowserPageWidget(_FakeWidget):
        def __init__(self, page, controller, navigate, **kwargs) -> None:
            super().__init__(
                page=page,
                controller=controller,
                navigate=navigate,
                **kwargs,
            )

    entity_module.EntityBrowserPageWidget = FakeEntityBrowserPageWidget
    monkeypatch.setitem(
        sys.modules,
        "eu5miner_gui.desktop.widgets.entity_browser_page",
        entity_module,
    )

    for module_name in (
        "eu5miner_gui.desktop.widgets.page_host",
        "eu5miner_gui.desktop.widgets.sidebar",
        "eu5miner_gui.desktop.widgets.source_bar",
    ):
        sys.modules.pop(module_name, None)

    page_host = importlib.import_module("eu5miner_gui.desktop.widgets.page_host")
    sidebar = importlib.import_module("eu5miner_gui.desktop.widgets.sidebar")
    source_bar = importlib.import_module("eu5miner_gui.desktop.widgets.source_bar")
    return page_host, sidebar, source_bar, FakeOverviewPageWidget, FakeEntityBrowserPageWidget


def _load_entity_browser_module(monkeypatch: pytest.MonkeyPatch):
    _install_fake_kivy(monkeypatch)
    _install_fake_visual_modules(monkeypatch)

    overview_module = ModuleType("eu5miner_gui.desktop.widgets.overview_page")

    class FakeOverviewPageWidget(_FakeWidget):
        def __init__(self, page, navigate, **kwargs) -> None:
            super().__init__(page=page, navigate=navigate, **kwargs)

    overview_module.OverviewPageWidget = FakeOverviewPageWidget
    monkeypatch.setitem(sys.modules, "eu5miner_gui.desktop.widgets.overview_page", overview_module)

    sys.modules.pop("eu5miner_gui.desktop.widgets.entity_browser_page", None)
    return importlib.import_module("eu5miner_gui.desktop.widgets.entity_browser_page")


def _load_sidebar_module(monkeypatch: pytest.MonkeyPatch):
    _install_fake_kivy(monkeypatch)
    _install_fake_visual_modules(monkeypatch)
    sys.modules.pop("eu5miner_gui.desktop.widgets.sidebar", None)
    return importlib.import_module("eu5miner_gui.desktop.widgets.sidebar")


def _find_widget(root: object, widget_type: type[Any]) -> Any | None:
    children = getattr(root, "children", ())
    for child in children:
        if isinstance(child, widget_type):
            return child
        nested = _find_widget(child, widget_type)
        if nested is not None:
            return nested
    return None


def test_source_bar_reset_to_auto_keeps_widget_tree_and_recovers_to_overview(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        page_host_module,
        sidebar_module,
        source_bar_module,
        fake_overview_widget,
        _,
    ) = _load_page_host_stack(monkeypatch)
    controller, fake_inspection = _controller(tmp_path)
    page_host = page_host_module.PageHost(controller=controller)
    sidebar = sidebar_module.Sidebar(controller=controller)
    sidebar.bind_page_host(page_host)
    source_bar = source_bar_module.SourceBar(controller=controller)
    source_bar.bind_page_host(page_host, sidebar)
    manual_root = tmp_path / "manual"
    manual_root.mkdir()

    source_bar._install_input.text = str(manual_root)
    source_bar._apply_install_root()
    controller.navigate(NavigationTarget.report("map"))
    page_host.refresh()
    fake_inspection.auto_discover_error = FileNotFoundError("No install was discovered.")

    source_bar._reset_to_auto()

    assert controller.navigation_state.current_target == NavigationTarget.overview()
    assert isinstance(page_host.children[0], fake_overview_widget)
    assert "No install was discovered." in source_bar._status_label.text
    assert source_bar._install_input.parent is not None
    assert len(source_bar.children) == 3


def test_page_host_routes_entity_pages_to_entity_browser_widget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        page_host_module,
        _sidebar_module,
        _source_bar_module,
        fake_overview_widget,
        fake_entity_widget,
    ) = _load_page_host_stack(monkeypatch)
    controller, _ = _controller(tmp_path)

    controller.navigate(NavigationTarget.entity_list("religion"))
    page_host = page_host_module.PageHost(controller=controller)
    assert isinstance(page_host.children[0], fake_entity_widget)

    controller.navigate(NavigationTarget.overview())
    page_host.refresh()
    assert isinstance(page_host.children[0], fake_overview_widget)


def test_entity_browser_page_builds_renderable_recycle_view(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entity_browser_module = _load_entity_browser_module(monkeypatch)
    controller, _ = _controller(tmp_path)
    controller.navigate(NavigationTarget.entity_list("religion"))
    page = controller.current_page()

    widget = entity_browser_module.EntityBrowserPageWidget(
        page=page,
        controller=controller,
        navigate=lambda _target: None,
    )
    entity_list = _find_widget(widget, entity_browser_module.EntityListView)

    assert entity_list is not None
    assert entity_list.layout_manager is not None
    assert entity_list.viewclass is entity_browser_module.EntityRowButton
    assert entity_list.layout_manager.viewclass is entity_browser_module.EntityRowButton
    assert len(entity_list.data) == 12
    assert entity_list.data[0]["entity_name"] == "faith_01"


def test_entity_browser_rows_define_explicit_visible_button_styling(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entity_browser_module = _load_entity_browser_module(monkeypatch)

    row = entity_browser_module.EntityRowButton(
        text="attack_threat",
        entity_name="attack_threat",
    )

    assert row.background_normal == ""
    assert row.background_down == ""
    assert row.color == (0.93, 0.95, 0.98, 1.0)
    assert row.background_color == (0.17, 0.2, 0.24, 1.0)
    row.is_selected = True
    row.on_is_selected()
    assert row.background_color == (0.28, 0.35, 0.42, 1.0)


def test_sidebar_entry_button_grows_for_wrapped_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sidebar_module = _load_sidebar_module(monkeypatch)
    button = sidebar_module.SidebarEntryButton(
        title="religion",
        subtitle=(
            "A deliberately long sidebar description that should wrap inside the "
            "button instead of overflowing its hitbox."
        ),
        size_hint_x=None,
        width=180,
    )

    assert button.height > 64
    assert button.height >= button.texture_size[1] + 18
