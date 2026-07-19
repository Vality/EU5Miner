"""Public testing utilities for the EU5Miner ecosystem.

These helpers are intended for use by:
- The library's own tests (``tests/``)
- Downstream consumer packages (``eu5miner-gui``, ``eu5miner-mcp``)
- Anyone writing integration or smoke tests against a synthetic EU5 install

They produce a small, deterministic filesystem layout under the supplied
``root`` directory. No real EU5 install is required.

Typical use::

    from pathlib import Path
    from eu5miner.testing import build_synthetic_install
    from eu5miner.inspection import inspect_install

    def test_my_feature(tmp_path: Path) -> None:
        install_root = tmp_path / "install"
        build_synthetic_install(install_root)
        summary = inspect_install(install_root)
        assert summary.root == install_root

The contract here is intentionally small and stable: changing the shape of the
returned ``GameInstall`` or the ``SyntheticCliSmokeSurface`` /
``SyntheticModWorkflowSurface`` dataclasses is a breaking change and will
require updating cross-package tests in ``eu5miner-gui`` and ``eu5miner-mcp``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eu5miner.source import ContentPhase, GameInstall


@dataclass(frozen=True)
class SyntheticCliSmokeSurface:
    """Minimal synthetic install plus a couple of representative files.

    Useful for CLI smoke tests that need to drive ``eu5miner`` against a
    known-good layout without a real EU5 install on disk.
    """

    install: GameInstall
    install_root: Path
    gui_relative_path: Path
    gui_file: Path
    script_file: Path


@dataclass(frozen=True)
class SyntheticModWorkflowSurface:
    """Synthetic install with a vanilla file plus a mod root and a content root.

    Used for mod workflow tests: planning and applying an override against a
    known vanilla file, with a second (later) mod that should be reported as
    ``blocked`` for one of the intended paths.
    """

    install: GameInstall
    install_root: Path
    vanilla_file: Path
    target_mod_root: Path
    later_mod_root: Path
    content_root: Path
    override_relative_path: Path
    blocked_relative_path: Path


def build_synthetic_install(install_root: Path) -> GameInstall:
    """Create an empty synthetic EU5 install layout under ``install_root``.

    The layout matches what ``GameInstall.discover`` expects:
    ``<install_root>/game/{loading_screen,main_menu,in_game}/`` plus
    ``<install_root>/game/{dlc,mod}/``. No representative files are written.
    """
    game_dir = install_root / "game"
    dlc_dir = game_dir / "dlc"
    mod_dir = game_dir / "mod"

    for phase_name in ("loading_screen", "main_menu", "in_game"):
        (game_dir / phase_name).mkdir(parents=True, exist_ok=True)
    dlc_dir.mkdir(parents=True, exist_ok=True)
    mod_dir.mkdir(parents=True, exist_ok=True)

    return GameInstall(
        root=install_root,
        game_dir=game_dir,
        dlc_dir=dlc_dir,
        mod_dir=mod_dir,
    )


def build_synthetic_cli_smoke_surface(root: Path) -> SyntheticCliSmokeSurface:
    """Create a synthetic install plus a couple of representative files.

    Writes a minimal ``in_game/gui/smoke.gui`` file inside the install and a
    standalone script file outside the install, returning the surface needed
    to drive ``eu5miner`` CLI commands against them.
    """
    install_root = root / "install"
    install = build_synthetic_install(install_root)
    gui_relative_path = Path("gui") / "smoke.gui"
    gui_file = install.phase_dir(ContentPhase.IN_GAME) / gui_relative_path
    script_file = root / "standalone_script.txt"

    _write_file(gui_file, "guiTypes = { widget = { name = smoke_widget } }\n")
    _write_file(script_file, "smoke_trigger = { always = yes }\n")

    return SyntheticCliSmokeSurface(
        install=install,
        install_root=install_root,
        gui_relative_path=gui_relative_path,
        gui_file=gui_file,
        script_file=script_file,
    )


def build_synthetic_mod_workflow_surface(root: Path) -> SyntheticModWorkflowSurface:
    """Create a synthetic install with a vanilla file plus a mod/content layout.

    The vanilla file lives at ``<install>/in_game/common/buildings/a.txt`` and
    is intended to be overridden by ``content_root`` when planning a mod update.
    A second, later mod (``later_mod_root``) shadows one path, so the planner
    should report that path as ``blocked`` rather than ``override``.
    """
    install_root = root / "install"
    install = build_synthetic_install(install_root)
    target_mod_root = root / "my_mod"
    later_mod_root = root / "late_mod"
    content_root = root / "content_root"
    override_relative_path = Path("common") / "buildings" / "a.txt"
    blocked_relative_path = Path("common") / "buildings" / "blocked.txt"

    vanilla_file = install.phase_dir(ContentPhase.IN_GAME) / override_relative_path
    _write_file(vanilla_file, "vanilla\n")
    _write_file(later_mod_root / "in_game" / blocked_relative_path, "late\n")

    _write_file(content_root / override_relative_path, "override = yes\n")
    _write_file(content_root / blocked_relative_path, "blocked = yes\n")

    return SyntheticModWorkflowSurface(
        install=install,
        install_root=install_root,
        vanilla_file=vanilla_file,
        target_mod_root=target_mod_root,
        later_mod_root=later_mod_root,
        content_root=content_root,
        override_relative_path=override_relative_path,
        blocked_relative_path=blocked_relative_path,
    )


def _write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


__all__ = [
    "SyntheticCliSmokeSurface",
    "SyntheticModWorkflowSurface",
    "build_synthetic_install",
    "build_synthetic_cli_smoke_surface",
    "build_synthetic_mod_workflow_surface",
]
