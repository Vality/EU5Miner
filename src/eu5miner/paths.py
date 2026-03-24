"""Install path resolution helpers."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_WINDOWS_INSTALL = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V"
)


def resolve_install_path(explicit: str | Path | None = None) -> Path:
    """Resolve the EU5 install path from an explicit value, env var, or default."""

    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(Path(explicit))

    env_value = os.environ.get("EU5_INSTALL_DIR")
    if env_value:
        candidates.append(Path(env_value))

    candidates.append(DEFAULT_WINDOWS_INSTALL)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]
