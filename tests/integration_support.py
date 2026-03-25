from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eu5miner.source import GameInstall


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


def build_synthetic_mod_workflow_surface(root: Path) -> SyntheticModWorkflowSurface:
    install_root = root / "install"
    game_dir = install_root / "game"
    dlc_dir = game_dir / "dlc"
    mod_dir = game_dir / "mod"
    target_mod_root = root / "my_mod"
    later_mod_root = root / "late_mod"
    content_root = root / "content_root"
    override_relative_path = Path("common") / "buildings" / "a.txt"
    blocked_relative_path = Path("common") / "buildings" / "blocked.txt"

    for phase_name in ("loading_screen", "main_menu", "in_game"):
        (game_dir / phase_name).mkdir(parents=True, exist_ok=True)
    dlc_dir.mkdir(parents=True, exist_ok=True)
    mod_dir.mkdir(parents=True, exist_ok=True)

    vanilla_file = game_dir / "in_game" / override_relative_path
    _write_file(vanilla_file, "vanilla\n")
    _write_file(later_mod_root / "in_game" / blocked_relative_path, "late\n")

    _write_file(content_root / override_relative_path, "override = yes\n")
    _write_file(content_root / blocked_relative_path, "blocked = yes\n")

    install = GameInstall(
        root=install_root,
        game_dir=game_dir,
        dlc_dir=dlc_dir,
        mod_dir=mod_dir,
    )
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
