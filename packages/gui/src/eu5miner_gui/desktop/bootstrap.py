from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from eu5miner_gui.desktop.controller import DesktopController
from eu5miner_gui.desktop.navigation import NavigationTarget

if TYPE_CHECKING:
    from typing import Any


@dataclass(frozen=True)
class DesktopLaunchOptions:
    install_root: Path | None = None
    initial_target: NavigationTarget = NavigationTarget.overview()
    mod_folders: tuple[Path, ...] = ()
    window_title: str = "EU5MinerGUI"


def launch_desktop_app(
    *,
    controller: DesktopController | None = None,
    options: DesktopLaunchOptions | None = None,
) -> int:
    os.environ.setdefault("KIVY_NO_ARGS", "1")
    desktop_controller = controller or DesktopController()
    launch_options = options or DesktopLaunchOptions()
    desktop_controller.initialize(
        initial_target=launch_options.initial_target,
        install_root=launch_options.install_root,
        mod_folders=launch_options.mod_folders,
    )

    from kivy.app import App
    from kivy.core.window import Window

    from eu5miner_gui.desktop.widgets.page_host import PageHost
    from eu5miner_gui.desktop.widgets.sidebar import Sidebar
    from eu5miner_gui.desktop.widgets.source_bar import SourceBar

    class EU5MinerDesktopApp(App):
        def build(self) -> Any:
            from kivy.uix.boxlayout import BoxLayout

            Window.minimum_width = 1100
            Window.minimum_height = 720
            self.title = launch_options.window_title
            root = BoxLayout(orientation="vertical", spacing=10, padding=10)
            source_bar = SourceBar(controller=desktop_controller)
            content = BoxLayout(orientation="horizontal", spacing=10)
            sidebar = Sidebar(controller=desktop_controller)
            page_host = PageHost(controller=desktop_controller)
            sidebar.bind_page_host(page_host)
            source_bar.bind_page_host(page_host, sidebar)
            content.add_widget(sidebar)
            content.add_widget(page_host)
            root.add_widget(source_bar)
            root.add_widget(content)
            return root

    EU5MinerDesktopApp().run()
    return 0
