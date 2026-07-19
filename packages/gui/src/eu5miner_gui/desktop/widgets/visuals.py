from __future__ import annotations

from typing import Any

from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from eu5miner_gui.desktop.adapters import SourceLayerViewModel, StatViewModel


def _bind_wrapped_text(
    widget: Label | Button,
    *,
    width_padding: int = 12,
    min_height: int = 24,
) -> None:
    def _update_text(*_: Any) -> None:
        widget.text_size = (max(widget.width - width_padding, 0), None)
        widget.texture_update()
        widget.height = max(min_height, int(widget.texture_size[1] + 14))

    widget.bind(size=_update_text, texture_size=_update_text, text=_update_text)
    _update_text()


def build_wrapped_label(
    text: str,
    *,
    markup: bool = False,
    halign: str = "left",
    valign: str = "middle",
    width: int | None = None,
    size_hint: tuple[float | None, float | None] = (1, None),
    min_height: int = 24,
    **kwargs: Any,
) -> Label:
    label = Label(
        text=text,
        markup=markup,
        halign=halign,
        valign=valign,
        size_hint=size_hint,
        **kwargs,
    )
    if width is not None:
        label.width = width
        label.size_hint_x = None
    _bind_wrapped_text(label, width_padding=12, min_height=min_height)
    return label


def build_wrapped_button(
    text: str,
    *,
    halign: str = "left",
    valign: str = "middle",
    width: int | None = None,
    size_hint: tuple[float | None, float | None] = (1, None),
    min_height: int = 34,
    width_padding: int = 24,
    **kwargs: Any,
) -> Button:
    button = Button(
        text=text,
        halign=halign,
        valign=valign,
        padding=(12, 8),
        size_hint=size_hint,
        **kwargs,
    )
    if width is not None:
        button.width = width
        button.size_hint_x = None
    _bind_wrapped_text(button, width_padding=width_padding, min_height=min_height)
    return button


def apply_card_background(
    widget: Widget,
    *,
    rgb: tuple[float, float, float],
    radius: float = 10.0,
) -> None:
    def _update_background(*_: Any) -> None:
        widget.canvas.before.clear()
        with widget.canvas.before:
            Color(rgb[0], rgb[1], rgb[2], 1.0)
            RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])

    widget.bind(pos=_update_background, size=_update_background)
    _update_background()


class StatChipRow(BoxLayout):
    def __init__(self, stats: tuple[StatViewModel, ...], **kwargs: Any) -> None:
        super().__init__(orientation="horizontal", spacing=8, size_hint_y=None, height=42, **kwargs)
        for stat in stats:
            chip = Label(
                text=f"[b]{stat.value}[/b]\n{stat.label}",
                markup=True,
                size_hint=(None, 1),
                width=max(160, 12 * len(stat.label)),
                halign="center",
                valign="middle",
            )
            chip.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
            apply_card_background(chip, rgb=(0.17, 0.23, 0.28), radius=12.0)
            self.add_widget(chip)


class SourceLayerStrip(BoxLayout):
    def __init__(self, layers: tuple[SourceLayerViewModel, ...], **kwargs: Any) -> None:
        super().__init__(orientation="horizontal", spacing=6, size_hint_y=None, height=52, **kwargs)
        palette = {
            "game": (0.18, 0.29, 0.32),
            "dlc": (0.27, 0.22, 0.14),
            "mod": (0.23, 0.16, 0.29),
        }
        for layer in layers:
            label = Label(
                text=f"[b]{layer.kind}:{layer.name}[/b]\nprio {layer.priority}",
                markup=True,
                size_hint=(1, 1),
                halign="center",
                valign="middle",
            )
            label.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
            apply_card_background(
                label,
                rgb=palette.get(layer.kind, (0.2, 0.2, 0.2)),
                radius=14.0,
            )
            self.add_widget(label)
