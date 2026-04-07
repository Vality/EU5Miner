from __future__ import annotations

from typing import Any

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from eu5miner_gui.desktop.controller import DesktopController
from .visuals import (
    apply_card_background,
    build_wrapped_button,
    build_wrapped_label,
)


class SourceBar(BoxLayout):
    def __init__(self, *, controller: DesktopController, **kwargs: Any) -> None:
        super().__init__(orientation="vertical", spacing=8, size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter("height"))
        self._controller = controller
        self._page_host = None
        self._sidebar = None
        self._install_input = TextInput(multiline=False, hint_text="Install root path")
        self._mod_input = TextInput(multiline=False, hint_text="Additional mod folder path")
        self._status_label = build_wrapped_label(
            text="",
            halign="left",
            valign="middle",
            min_height=28,
        )
        self._remove_mod_button: Button | None = None
        apply_card_background(self, rgb=(0.1, 0.11, 0.14))
        self._build_once()
        self.refresh()

    def bind_page_host(self, page_host: Any, sidebar: Any) -> None:
        self._page_host = page_host
        self._sidebar = sidebar

    def refresh(self) -> None:
        self._sync_state()

    def _build_once(self) -> None:
        controls = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None)
        controls.bind(minimum_height=controls.setter("height"))
        set_install_button = build_wrapped_button(
            text="Use install root",
            size_hint=(None, 1),
            width=150,
        )
        auto_button = build_wrapped_button(
            text="Auto",
            size_hint=(None, 1),
            width=80,
        )
        reload_button = build_wrapped_button(
            text="Reload",
            size_hint=(None, 1),
            width=90,
        )
        set_install_button.bind(on_release=lambda *_: self._apply_install_root())
        auto_button.bind(on_release=lambda *_: self._reset_to_auto())
        reload_button.bind(on_release=lambda *_: self._reload())
        install_label = build_wrapped_label(
            text="Install",
            size_hint=(None, 1),
            width=56,
            halign="left",
            valign="middle",
            min_height=24,
        )
        controls.add_widget(install_label)
        controls.add_widget(self._install_input)
        controls.add_widget(set_install_button)
        controls.add_widget(auto_button)
        controls.add_widget(reload_button)
        self.add_widget(controls)

        mods = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None)
        mods.bind(minimum_height=mods.setter("height"))
        add_mod_button = build_wrapped_button(
            text="Add mod folder",
            size_hint=(None, 1),
            width=140,
        )
        remove_mod_button = build_wrapped_button(
            text="Remove selected",
            size_hint=(None, 1),
            width=140,
        )
        self._remove_mod_button = remove_mod_button
        add_mod_button.bind(on_release=lambda *_: self._add_mod_folder())
        remove_mod_button.bind(on_release=lambda *_: self._remove_mod_folder())
        mods_label = build_wrapped_label(
            text="Mods",
            size_hint=(None, 1),
            width=56,
            halign="left",
            valign="middle",
            min_height=24,
        )
        mods.add_widget(mods_label)
        mods.add_widget(self._mod_input)
        mods.add_widget(add_mod_button)
        mods.add_widget(remove_mod_button)
        self.add_widget(mods)

        self._status_label.bind(
            size=lambda instance, _: setattr(instance, "text_size", instance.size)
        )
        self.add_widget(self._status_label)

    def _apply_install_root(self) -> None:
        self._controller.set_manual_install_root(self._install_input.text)
        self._refresh_views()

    def _reset_to_auto(self) -> None:
        self._controller.set_manual_install_root(None)
        self._refresh_views()

    def _reload(self) -> None:
        self._controller.reload()
        self._refresh_views()

    def _add_mod_folder(self) -> None:
        if not self._mod_input.text.strip():
            return
        self._controller.add_mod_folder(self._mod_input.text)
        self._mod_input.text = ""
        self._refresh_views()

    def _remove_mod_folder(self) -> None:
        self._controller.remove_selected_mod_folder()
        self._refresh_views()

    def _refresh_views(self) -> None:
        self.refresh()
        if self._sidebar is not None:
            self._sidebar.refresh()
        if self._page_host is not None:
            self._page_host.refresh()

    def _sync_state(self) -> None:
        current_install_root = (
            self._controller.active_install_root
            or self._controller.source_state.manual_install_root
        )
        install_text = str(current_install_root or "")
        if self._install_input.text != install_text:
            self._install_input.text = install_text
        self._status_label.text = self._status_text()
        if self._remove_mod_button is not None:
            self._remove_mod_button.disabled = (
                self._controller.ui_state.selected_mod_folder is None
            )

    def _status_text(self) -> str:
        active_root = self._controller.active_install_root
        mod_folders = self._controller.active_mod_folders
        mod_text = ", ".join(path.name for path in mod_folders) if mod_folders else "none"
        if self._controller.source_state.error_message is not None:
            return (
                f"Status: {self._controller.source_state.load_status}. "
                f"Install={active_root or 'none'}. Mods={mod_text}. "
                f"Message={self._controller.source_state.error_message}"
            )
        return (
            f"Status: {self._controller.source_state.load_status}. "
            f"Install={active_root or 'none'}. Mods={mod_text}."
        )
