from __future__ import annotations

from typing import Any

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from eu5miner_gui.desktop.adapters import TextPageViewModel
from eu5miner_gui.desktop.widgets.overview_page import OverviewPageWidget


class ReportPageWidget(OverviewPageWidget):
    pass


class HelperPageWidget(OverviewPageWidget):
    pass


def build_primary_link_button(page: TextPageViewModel, navigate: Any) -> BoxLayout | None:
    if page.primary_link is None:
        return None
    container = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=40)
    label = Label(
        text="Related navigation",
        size_hint=(None, 1),
        width=160,
        halign="left",
        valign="middle",
    )
    label.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
    button = Button(text=page.primary_link.page_key, size_hint=(None, 1), width=220)
    button.bind(on_release=lambda *_: navigate(page.primary_link))
    container.add_widget(label)
    container.add_widget(button)
    return container
