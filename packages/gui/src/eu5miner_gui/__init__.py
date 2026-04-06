"""EU5MinerGUI public package exports."""

from eu5miner_gui.app import (
    build_navigation_target,
    build_shell_message,
    launch_app,
    launch_desktop,
    list_supported_system_names,
)
from eu5miner_gui.browser import BrowserModel, BrowserPage, BrowserSection, build_browser_model
from eu5miner_gui.desktop import DesktopController

__all__ = [
	"BrowserModel",
	"BrowserPage",
	"BrowserSection",
	"DesktopController",
	"build_browser_model",
	"build_navigation_target",
	"build_shell_message",
	"launch_app",
	"launch_desktop",
	"list_supported_system_names",
]
