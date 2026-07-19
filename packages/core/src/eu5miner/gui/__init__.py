"""eu5miner-gui public exports.

These symbols are only importable when the package is installed with the
``[gui]`` extra (``pip install eu5miner[gui]``).
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

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


_ORIGIN = {
    "BrowserModel": "browser",
    "BrowserPage": "browser",
    "BrowserSection": "browser",
    "DesktopController": "desktop.controller",
    "build_browser_model": "browser",
    "build_navigation_target": "app",
    "build_shell_message": "app",
    "launch_app": "app",
    "launch_desktop": "app",
    "list_supported_system_names": "app",
}


def __getattr__(name: str) -> Any:
    if name in __all__:
        try:
            mod = import_module(f"eu5miner.gui.{_ORIGIN[name]}")
        except ImportError as exc:
            raise ImportError(
                f"'{name}' requires the 'eu5miner[gui]' extra. "
                "Install it with: pip install eu5miner[gui]"
            ) from exc
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(name)
