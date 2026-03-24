from __future__ import annotations

from pathlib import Path

from eu5miner.source import ContentPhase, GameInstall
from eu5miner.vfs import ContentSource, SourceKind, VirtualFilesystem


def _write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_vfs_last_source_wins_for_matching_phase_file(tmp_path: Path) -> None:
    vanilla_root = tmp_path / "vanilla"
    dlc_root = tmp_path / "dlc_pack"
    mod_root = tmp_path / "my_mod"

    relative_file = Path("in_game") / "common" / "buildings" / "sample.txt"
    _write_file(vanilla_root / relative_file, "vanilla")
    _write_file(dlc_root / relative_file, "dlc")
    _write_file(mod_root / relative_file, "mod")

    vfs = VirtualFilesystem(
        [
            ContentSource("vanilla", SourceKind.VANILLA, vanilla_root, 0),
            ContentSource("dlc_pack", SourceKind.DLC, dlc_root, 10),
            ContentSource("my_mod", SourceKind.MOD, mod_root, 100),
        ]
    )

    merged = vfs.get_merged_file(ContentPhase.IN_GAME, Path("common") / "buildings" / "sample.txt")

    assert merged is not None
    assert merged.winner.source.name == "my_mod"
    assert [file.source.name for file in merged.contributors] == ["vanilla", "dlc_pack", "my_mod"]


def test_vfs_keeps_phase_separate(tmp_path: Path) -> None:
    source_root = tmp_path / "vanilla"
    shared_relative = Path("common") / "sample.txt"

    _write_file(source_root / "loading_screen" / shared_relative, "loading")
    _write_file(source_root / "main_menu" / shared_relative, "menu")

    vfs = VirtualFilesystem([ContentSource("vanilla", SourceKind.VANILLA, source_root, 0)])

    loading = vfs.get_merged_file(ContentPhase.LOADING_SCREEN, shared_relative)
    menu = vfs.get_merged_file(ContentPhase.MAIN_MENU, shared_relative)

    assert loading is not None
    assert menu is not None
    assert loading.winner.absolute_path.read_text(encoding="utf-8") == "loading"
    assert menu.winner.absolute_path.read_text(encoding="utf-8") == "menu"


def test_vfs_from_install_discovers_vanilla_and_dlc_sources(game_install: GameInstall) -> None:
    vfs = VirtualFilesystem.from_install(game_install)

    kinds = [source.kind for source in vfs.sources]
    assert SourceKind.VANILLA in kinds
    assert SourceKind.DLC in kinds
    assert vfs.sources[0].name == "vanilla"


def test_vfs_can_resolve_real_gui_sample(game_install: GameInstall) -> None:
    vfs = VirtualFilesystem.from_install(game_install)

    merged = vfs.get_merged_file(ContentPhase.IN_GAME, Path("gui") / "agenda_view.gui")

    assert merged is not None
    assert merged.winner.absolute_path.exists()
    assert merged.winner.source.kind in {SourceKind.VANILLA, SourceKind.DLC}
