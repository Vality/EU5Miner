from __future__ import annotations

from typing import Any

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from eu5miner_gui.desktop.controller import DesktopController
from eu5miner_gui.desktop.widgets.visuals import apply_card_background


class SourceBar(BoxLayout):
    def __init__(self, *, controller: DesktopController, **kwargs: Any) -> None:
        super().__init__(orientation="vertical", spacing=8, size_hint_y=None, height=118, **kwargs)
        self._controller = controller
        self._page_host = None
        self._sidebar = None
        self._install_input = TextInput(multiline=False, hint_text="Install root path")
        self._mod_input = TextInput(multiline=False, hint_text="Additional mod folder path")
        apply_card_background(self, rgb=(0.1, 0.11, 0.14))
        self._rebuild()

    def bind_page_host(self, page_host: Any, sidebar: Any) -> None:
        self._page_host = page_host
        self._sidebar = sidebar

    def refresh(self) -> None:
        self.clear_widgets()
        self._rebuild()

    def _rebuild(self) -> None:
        controls = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=40)
        current_install_root = (
            self._controller.active_install_root
            or self._controller.source_state.manual_install_root
        )
        self._install_input.text = str(current_install_root or "")
        set_install_button = Button(text="Use install root", size_hint=(None, 1), width=150)
        auto_button = Button(text="Auto", size_hint=(None, 1), width=80)
        reload_button = Button(text="Reload", size_hint=(None, 1), width=90)
        set_install_button.bind(on_release=lambda *_: self._apply_install_root())
        auto_button.bind(on_release=lambda *_: self._reset_to_auto())
        reload_button.bind(on_release=lambda *_: self._reload())
        install_label = Label(
            text="Install",
            size_hint=(None, 1),
            width=56,
            halign="left",
            valign="middle",
        )
        install_label.bind(
            size=lambda instance, _: setattr(instance, "text_size", instance.size)
        )
        controls.add_widget(install_label)
        controls.add_widget(self._install_input)
        controls.add_widget(set_install_button)
        controls.add_widget(auto_button)
        controls.add_widget(reload_button)
        self.add_widget(controls)

        mods = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=36)
        add_mod_button = Button(text="Add mod folder", size_hint=(None, 1), width=140)
        remove_mod_button = Button(text="Remove selected", size_hint=(None, 1), width=140)
        add_mod_button.bind(on_release=lambda *_: self._add_mod_folder())
        remove_mod_button.bind(on_release=lambda *_: self._remove_mod_folder())
        mods_label = Label(
            text="Mods",
            size_hint=(None, 1),
            width=56,
            halign="left",
            valign="middle",
        )
        mods_label.bind(
            size=lambda instance, _: setattr(instance, "text_size", instance.size)
        )
        mods.add_widget(mods_label)
        mods.add_widget(self._mod_input)
        mods.add_widget(add_mod_button)
        mods.add_widget(remove_mod_button)
        self.add_widget(mods)

        status = Label(
            text=self._status_text(),
            size_hint_y=None,
            height=28,
            halign="left",
            valign="middle",
        )
        status.bind(size=lambda instance, _: setattr(instance, "text_size", instance.size))
        self.add_widget(status)

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
