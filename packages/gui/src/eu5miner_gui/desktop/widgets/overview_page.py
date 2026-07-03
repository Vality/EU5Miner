from __future__ import annotations

from typing import Any

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from eu5miner_gui.desktop.adapters import LinkItemViewModel, SectionViewModel, TextPageViewModel
from .visuals import (
    SourceLayerStrip,
    StatChipRow,
    apply_card_background,
    build_wrapped_button,
    build_wrapped_label,
)


class OverviewPageWidget(ScrollView):
    def __init__(self, page: TextPageViewModel, navigate: Any, **kwargs: Any) -> None:
        super().__init__(do_scroll_x=False, **kwargs)
        self.bar_width = 8
        content = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(_build_header(page))
        if page.source_layers:
            content.add_widget(SourceLayerStrip(page.source_layers))
        if page.stats:
            content.add_widget(StatChipRow(page.stats))
        for section in page.sections:
            content.add_widget(_build_section(section, navigate))
        self.add_widget(content)


class _ClickableLabel(Label):
    pass


def _build_header(page: TextPageViewModel) -> BoxLayout:
    header = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
    header.bind(minimum_height=header.setter("height"))
    title = build_wrapped_label(
        text=f"[b]{page.title}[/b]",
        markup=True,
        halign="left",
        valign="middle",
        min_height=36,
    )
    description = build_wrapped_label(
        text=page.description,
        halign="left",
        valign="middle",
        min_height=28,
    )
    header.add_widget(title)
    header.add_widget(description)
    if page.notice is not None:
        notice = build_wrapped_label(
            text=f"[color=ffcc80]{page.notice}[/color]",
            markup=True,
            halign="left",
            valign="middle",
            min_height=30,
        )
        header.add_widget(notice)
    return header


def _build_section(section: SectionViewModel, navigate: Any) -> BoxLayout:
    section_box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, padding=10)
    section_box.bind(minimum_height=section_box.setter("height"))
    apply_card_background(section_box, rgb=(0.12, 0.14, 0.16))
    title = build_wrapped_label(
        text=f"[b]{section.title}[/b]",
        markup=True,
        halign="left",
        valign="middle",
        min_height=28,
    )
    section_box.add_widget(title)
    for item in section.items:
        section_box.add_widget(_build_item(item, navigate))
    return section_box


def _build_item(item: LinkItemViewModel, navigate: Any) -> Label:
    if item.target is None:
        return build_wrapped_label(
            text=item.text,
            halign="left",
            valign="middle",
            min_height=26,
        )

    button = build_wrapped_button(
        text=item.text,
        halign="left",
        valign="middle",
        min_height=34,
    )
    button.bind(on_release=lambda *_: navigate(item.target))
    return button
