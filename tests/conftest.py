from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.paths import resolve_install_path
from eu5miner.source import GameInstall
from tests.integration_support import (
    SyntheticModWorkflowSurface,
    build_synthetic_mod_workflow_surface,
)


@pytest.fixture(scope="session")
def install_path() -> Path:
    return resolve_install_path()


@pytest.fixture(scope="session")
def game_install(install_path: Path) -> GameInstall:
    if not install_path.exists():
        pytest.skip("EU5 install path is unavailable")
    return GameInstall.discover(install_path)


@pytest.fixture
def synthetic_mod_workflow_surface(tmp_path: Path) -> SyntheticModWorkflowSurface:
    return build_synthetic_mod_workflow_surface(tmp_path)
