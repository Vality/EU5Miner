"""Desktop application package for the real Kivy GUI."""

from eu5miner.gui.desktop.bootstrap import launch_desktop_app
from eu5miner.gui.desktop.controller import DesktopController
from eu5miner.gui.desktop.navigation import NavigationTarget, NavigationTargetKind

__all__ = [
    "DesktopController",
    "NavigationTarget",
    "NavigationTargetKind",
    "launch_desktop_app",
]
