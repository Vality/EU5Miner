from __future__ import annotations

from typing import Any

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

from eu5miner_gui.desktop.adapters import EntityBrowserPageViewModel
from eu5miner_gui.desktop.controller import DesktopController
from eu5miner_gui.desktop.navigation import NavigationTarget
from eu5miner_gui.desktop.widgets.entity_browser_page import EntityBrowserPageWidget
from eu5miner_gui.desktop.widgets.overview_page import OverviewPageWidget
from eu5miner_gui.desktop.widgets.report_page import HelperPageWidget, ReportPageWidget


class PageHost(BoxLayout):
    def __init__(self, *, controller: DesktopController, **kwargs: Any) -> None:
        super().__init__(orientation="vertical", size_hint=(0.76, 1), **kwargs)
        self._controller = controller
        self._refresh_event = None
        self.refresh()

    def refresh(self) -> None:
        if self._refresh_event is not None:
            self._refresh_event.cancel()
        self.clear_widgets()
        page = self._controller.current_page()
        if isinstance(page, EntityBrowserPageViewModel):
            self.add_widget(
                EntityBrowserPageWidget(
                    page=page,
                    controller=self._controller,
                    navigate=self.navigate,
                )
            )
        elif page.kind == "overview":
            self.add_widget(OverviewPageWidget(page, self.navigate))
        elif page.kind == "helper":
            self.add_widget(HelperPageWidget(page, self.navigate))
        else:
            self.add_widget(ReportPageWidget(page, self.navigate))
        self._refresh_event = Clock.schedule_once(self._post_build_refresh, 0)

    def _post_build_refresh(self, *_: Any) -> None:
        self.do_layout()

    def navigate(self, target: NavigationTarget) -> None:
        self._controller.navigate(target)
        self.refresh()
