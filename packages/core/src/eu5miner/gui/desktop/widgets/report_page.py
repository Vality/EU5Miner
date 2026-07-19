from __future__ import annotations

from typing import Any

from kivy.uix.boxlayout import BoxLayout

from eu5miner.gui.desktop.adapters import TextPageViewModel
from eu5miner.gui.desktop.widgets.overview_page import OverviewPageWidget

from .visuals import build_wrapped_button, build_wrapped_label


class ReportPageWidget(OverviewPageWidget):
    pass


class HelperPageWidget(OverviewPageWidget):
    pass


def build_primary_link_button(page: TextPageViewModel, navigate: Any) -> BoxLayout | None:
    if page.primary_link is None:
        return None
    container = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None)
    container.bind(minimum_height=container.setter("height"))
    label = build_wrapped_label(
        text="Related navigation",
        size_hint=(None, 1),
        width=160,
        halign="left",
        valign="middle",
        min_height=24,
    )
    button = build_wrapped_button(
        text=page.primary_link.page_key,
        size_hint=(None, 1),
        width=220,
        min_height=34,
    )
    button.bind(on_release=lambda *_: navigate(page.primary_link))
    container.add_widget(label)
    container.add_widget(button)
    return container
