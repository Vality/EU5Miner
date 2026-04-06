from __future__ import annotations

from typing import Any

from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from eu5miner_gui.desktop.controller import DesktopController
from eu5miner_gui.desktop.navigation import NavigationTarget
from eu5miner_gui.desktop.widgets.visuals import apply_card_background


class Sidebar(BoxLayout):
    def __init__(self, *, controller: DesktopController, **kwargs: Any) -> None:
        super().__init__(orientation="vertical", size_hint=(0.24, 1), **kwargs)
        self._controller = controller
        self._page_host = None
        apply_card_background(self, rgb=(0.08, 0.09, 0.11))
        self._build_sidebar()

    def bind_page_host(self, page_host: Any) -> None:
        self._page_host = page_host

    def refresh(self) -> None:
        self.clear_widgets()
        self._build_sidebar()

    def _build_sidebar(self) -> None:
        title = Label(
            text="[b]EU5MinerGUI[/b]",
            markup=True,
            size_hint_y=None,
            height=40,
            halign="center",
            valign="middle",
        )
        title.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
        self.add_widget(title)
        accordion = Accordion(orientation="vertical")
        for section in self._controller.sidebar_sections():
            item = AccordionItem(title=section.title)
            body = ScrollView(do_scroll_x=False)
            layout = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, padding=6)
            layout.bind(minimum_height=layout.setter("height"))
            for entry in section.items:
                button = Button(
                    text=f"{entry.title}\n{entry.subtitle}",
                    markup=False,
                    size_hint_y=None,
                    height=56,
                    halign="left",
                    valign="middle",
                )
                button.bind(
                    size=lambda instance, _: setattr(
                        instance,
                        "text_size",
                        (instance.width - 18, None),
                    )
                )
                button.bind(on_release=lambda *_args, target=entry.target: self._navigate(target))
                layout.add_widget(button)
            body.add_widget(layout)
            item.add_widget(body)
            accordion.add_widget(item)
        self.add_widget(accordion)

    def _navigate(self, target: NavigationTarget) -> None:
        self._controller.navigate(target)
        if self._page_host is not None:
            self._page_host.refresh()
