"""eu5miner-mcp public exports.

These symbols are only importable when the package is installed with the
``[mcp]`` extra (``pip install eu5miner[mcp]``).
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["build_startup_message", "run_server", "run_stdio_server", "serve_stdio"]


_ORIGIN = {
    "build_startup_message": "server",
    "run_server": "server",
    "run_stdio_server": "transport",
    "serve_stdio": "transport",
}


def __getattr__(name: str) -> Any:
    if name in __all__:
        try:
            mod = import_module(f"eu5miner.mcp.{_ORIGIN[name]}")
        except ImportError as exc:
            raise ImportError(
                f"'{name}' requires the 'eu5miner[mcp]' extra. "
                "Install it with: pip install eu5miner[mcp]"
            ) from exc
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(name)
