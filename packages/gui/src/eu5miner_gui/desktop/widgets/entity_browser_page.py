from __future__ import annotations

from typing import Any

from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from eu5miner_gui.desktop.adapters import EntityBrowserPageViewModel
from eu5miner_gui.desktop.navigation import NavigationTarget
from eu5miner_gui.desktop.widgets.overview_page import OverviewPageWidget

from .visuals import apply_card_background


class EntityRowButton(RecycleDataViewBehavior, Button):
    index = NumericProperty(-1)
    callback = ObjectProperty(None, allownone=True)
    entity_name = StringProperty("")
    is_selected = BooleanProperty(False)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=38,
            padding=(12, 8),
            background_normal="",
            background_down="",
            background_disabled_normal="",
            background_disabled_down="",
            color=(0.93, 0.95, 0.98, 1.0),
            **kwargs,
        )
        self.bind(size=self._update_text_size)
        self._update_text_size()
        self.on_is_selected()

    def _update_text_size(self, *_: Any) -> None:
        self.text_size = (max(self.width - 24, 0), None)

    def refresh_view_attrs(
        self,
        rv: RecycleView,
        index: int,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        self.index = index
        refreshed = super().refresh_view_attrs(rv, index, data)
        self._update_text_size()
        self.on_is_selected()
        return refreshed

    def on_is_selected(self, *_: Any) -> None:
        self.background_color = (
            (0.28, 0.35, 0.42, 1.0)
            if self.is_selected
            else (0.17, 0.2, 0.24, 1.0)
        )

    def on_release(self) -> None:
        if self.callback is not None:
            self.callback(self.entity_name)


class EntityListView(RecycleView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.viewclass = EntityRowButton
        self.bar_width = 8
        layout = RecycleBoxLayout(
            default_size=(None, 38),
            default_size_hint=(1, None),
            size_hint=(1, None),
            orientation="vertical",
            spacing=4,
        )
        layout.viewclass = EntityRowButton
        layout.bind(minimum_height=layout.setter("height"))
        self.add_widget(layout)
        self.layout_manager = layout


class EntityBrowserPageWidget(BoxLayout):
    def __init__(
        self,
        *,
        page: EntityBrowserPageViewModel,
        controller: Any,
        navigate: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(orientation="horizontal", spacing=10, **kwargs)
        self._controller = controller
        self._navigate = navigate
        self._page = page
        self._search_event = None
        self.add_widget(self._build_list_panel(page))
        self.add_widget(self._build_detail_panel(page, navigate))

    def _build_list_panel(self, page: EntityBrowserPageViewModel) -> BoxLayout:
        panel = BoxLayout(orientation="vertical", spacing=8, size_hint=(0.48, 1))
        apply_card_background(panel, rgb=(0.12, 0.14, 0.16))
        title = Label(
            text=f"[b]{page.title}[/b]",
            markup=True,
            size_hint_y=None,
            height=34,
            halign="left",
            valign="middle",
        )
        title.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
        panel.add_widget(title)
        controls = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=38,
        )
        search_input = TextInput(
            text=page.search_text,
            multiline=False,
            hint_text="Search entities",
        )
        search_input.bind(text=self._schedule_search)
        sort_spinner = Spinner(
            text=page.sort_mode,
            values=("name", "group", "source"),
            size_hint=(None, 1),
            width=120,
        )
        sort_spinner.bind(text=lambda _, value: self._set_sort(page.system, value))
        controls.add_widget(search_input)
        controls.add_widget(sort_spinner)
        panel.add_widget(controls)
        count_label = Label(
            text=self._count_text(page),
            size_hint_y=None,
            height=24,
            halign="left",
            valign="middle",
        )
        count_label.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
        panel.add_widget(count_label)
        if page.empty_message is not None and not page.rows:
            empty_label = Label(
                text=page.empty_message,
                size_hint_y=None,
                height=32,
                halign="left",
                valign="middle",
            )
            empty_label.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
            panel.add_widget(empty_label)
            return panel
        entity_list = EntityListView()
        entity_list.data = [
            {
                "text": row.label,
                "entity_name": row.name,
                "callback": (
                    lambda entity_name, system=page.system: self._select_entity(
                        system,
                        entity_name,
                    )
                ),
                "is_selected": row.name == page.selected_entity_name,
                "size_hint_y": None,
                "height": 38,
            }
            for row in page.rows
        ]
        panel.add_widget(entity_list)
        return panel

    def _build_detail_panel(self, page: EntityBrowserPageViewModel, navigate: Any) -> BoxLayout:
        panel = BoxLayout(orientation="vertical", size_hint=(0.52, 1))
        apply_card_background(panel, rgb=(0.09, 0.1, 0.12))
        if page.detail is None:
            label = Label(
                text=page.empty_message or "Select an entity to load its detail.",
                halign="center",
                valign="middle",
            )
            label.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
            panel.add_widget(label)
            return panel
        panel.add_widget(OverviewPageWidget(page.detail, navigate))
        return panel

    def _schedule_search(self, _: TextInput, value: str) -> None:
        if self._search_event is not None:
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(
            lambda *_: self._apply_search(value),
            0.2,
        )

    def _apply_search(self, value: str) -> None:
        self._controller.set_entity_search_text(self._page.system, value)
        self._navigate(NavigationTarget.entity_list(self._page.system))

    def _set_sort(self, system: str, value: str) -> None:
        self._controller.set_entity_sort_mode(system, value)
        self._navigate(NavigationTarget.entity_list(system))

    def _select_entity(self, system: str, entity_name: str) -> None:
        self._controller.set_selected_entity(system, entity_name)
        self._navigate(NavigationTarget.entity_detail(system, entity_name))

    def _count_text(self, page: EntityBrowserPageViewModel) -> str:
        return f"Showing {page.visible_count} result(s) for {page.system}."
