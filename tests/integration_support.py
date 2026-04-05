from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eu5miner.source import ContentPhase, GameInstall


@dataclass(frozen=True)
class SyntheticCliSmokeSurface:
    install: GameInstall
    install_root: Path
    gui_relative_path: Path
    gui_file: Path
    script_file: Path


@dataclass(frozen=True)
class SyntheticModWorkflowSurface:
    install: GameInstall
    install_root: Path
    vanilla_file: Path
    target_mod_root: Path
    later_mod_root: Path
    content_root: Path
    override_relative_path: Path
    blocked_relative_path: Path


def build_synthetic_install(install_root: Path) -> GameInstall:
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
