from __future__ import annotations

import os

os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_WINDOW", "mock")
os.environ.setdefault("KIVY_GL_BACKEND", "mock")
os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")

from pathlib import Path

import pytest

from eu5miner.paths import resolve_install_path
from eu5miner.source import GameInstall
from tests.integration_support import (
    SyntheticCliSmokeSurface,
    SyntheticModWorkflowSurface,
    build_synthetic_cli_smoke_surface,
    build_synthetic_mod_workflow_surface,
)


def pytest_configure(config: pytest.Config) -> None:
    if not config.pluginmanager.hasplugin("timeout"):
        return

    config.option.timeout = 30
    config.option.timeout_method = "thread"


@pytest.fixture(scope="session")
def install_path() -> Path:
    return resolve_install_path()


@pytest.fixture(scope="session")
def game_install(install_path: Path) -> GameInstall:
    if not install_path.exists():
        pytest.skip("EU5 install path is unavailable")
    return GameInstall.discover(install_path)


@pytest.fixture
def synthetic_cli_smoke_surface(tmp_path: Path) -> SyntheticCliSmokeSurface:
    return build_synthetic_cli_smoke_surface(tmp_path)


@pytest.fixture
def synthetic_mod_workflow_surface(tmp_path: Path) -> SyntheticModWorkflowSurface:
    return build_synthetic_mod_workflow_surface(tmp_path)
