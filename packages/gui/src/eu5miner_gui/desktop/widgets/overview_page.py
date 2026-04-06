from __future__ import annotations

from typing import Any

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from eu5miner_gui.desktop.adapters import LinkItemViewModel, SectionViewModel, TextPageViewModel
from eu5miner_gui.desktop.widgets.visuals import (
    SourceLayerStrip,
    StatChipRow,
    apply_card_background,
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
    header = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, height=100)
    title = Label(
        text=f"[b]{page.title}[/b]",
        markup=True,
        size_hint_y=None,
        height=36,
        halign="left",
        valign="middle",
    )
    title.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
    description = Label(
        text=page.description,
        size_hint_y=None,
        height=28,
        halign="left",
        valign="middle",
    )
    description.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
    header.add_widget(title)
    header.add_widget(description)
    if page.notice is not None:
        notice = Label(
            text=f"[color=ffcc80]{page.notice}[/color]",
            markup=True,
            size_hint_y=None,
            height=30,
            halign="left",
            valign="middle",
        )
        notice.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
        header.add_widget(notice)
        header.height += 30
    return header


def _build_section(section: SectionViewModel, navigate: Any) -> BoxLayout:
    section_box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, padding=10)
    section_box.bind(minimum_height=section_box.setter("height"))
    apply_card_background(section_box, rgb=(0.12, 0.14, 0.16))
    title = Label(
        text=f"[b]{section.title}[/b]",
        markup=True,
        size_hint_y=None,
        height=28,
        halign="left",
        valign="middle",
    )
    title.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
    section_box.add_widget(title)
    for item in section.items:
        section_box.add_widget(_build_item(item, navigate))
    return section_box


def _build_item(item: LinkItemViewModel, navigate: Any) -> Label:
    if item.target is None:
        label = Label(
            text=item.text,
            size_hint_y=None,
            height=26,
            halign="left",
            valign="middle",
        )
        label.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
        return label
    from kivy.uix.button import Button

    button = Button(
        text=item.text,
        size_hint_y=None,
        height=34,
        halign="left",
        valign="middle",
    )
    button.text_size = (button.width - 24, None)
    button.bind(
        size=lambda instance, _: setattr(
            instance,
            "text_size",
            (instance.width - 24, None),
        )
    )
    button.bind(on_release=lambda *_: navigate(item.target))
    return button
