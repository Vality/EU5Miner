from __future__ import annotations

from pathlib import Path

from eu5miner.source import ContentPhase, GameInstall
from eu5miner.vfs import ContentSource, ReplacePathRule, SourceKind, VirtualFilesystem


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


def test_vfs_replace_path_hides_lower_priority_subtree_files(tmp_path: Path) -> None:
    vanilla_root = tmp_path / "vanilla"
    mod_root = tmp_path / "my_mod"

    _write_file(vanilla_root / "in_game" / "common" / "buildings" / "a.txt", "vanilla a")
    _write_file(mod_root / "in_game" / "common" / "buildings" / "b.txt", "mod b")

    vfs = VirtualFilesystem(
        [
            ContentSource("vanilla", SourceKind.VANILLA, vanilla_root, 0),
            ContentSource(
                "my_mod",
                SourceKind.MOD,
                mod_root,
                100,
                replace_rules=(
                    ReplacePathRule(
                        phase=ContentPhase.IN_GAME,
                        relative_root=Path("common") / "buildings",
                        raw_path="game/in_game/common/buildings",
                    ),
                ),
            ),
        ]
    )

    merged = vfs.merge_phase(ContentPhase.IN_GAME, Path("common") / "buildings")

    assert [file.relative_path for file in merged] == [Path("common") / "buildings" / "b.txt"]
    assert merged[0].winner.source.name == "my_mod"


def test_vfs_plan_write_detects_higher_priority_replace_path_blocker(tmp_path: Path) -> None:
    vanilla_root = tmp_path / "vanilla"
    mod_root = tmp_path / "my_mod"

    _write_file(mod_root / "in_game" / "common" / "buildings" / "existing.txt", "mod")

    vfs = VirtualFilesystem(
        [
            ContentSource("vanilla", SourceKind.VANILLA, vanilla_root, 0),
            ContentSource(
                "my_mod",
                SourceKind.MOD,
                mod_root,
                100,
                replace_rules=(
                    ReplacePathRule(
                        phase=ContentPhase.IN_GAME,
                        relative_root=Path("common") / "buildings",
                        raw_path="game/in_game/common/buildings",
                    ),
                ),
            ),
        ]
    )

    plan = vfs.plan_write(
        "vanilla",
        ContentPhase.IN_GAME,
        Path("common") / "buildings" / "planned.txt",
    )

    assert plan.is_visible is False
    assert len(plan.blockers) == 1
    assert plan.blockers[0].source.name == "my_mod"
    assert plan.blockers[0].reason == "replace_path"
    assert plan.blockers[0].replace_rule is not None


def test_vfs_plan_write_reports_visible_override_against_lower_priority_file(
    tmp_path: Path,
) -> None:
    vanilla_root = tmp_path / "vanilla"
    mod_root = tmp_path / "my_mod"

    _write_file(vanilla_root / "in_game" / "common" / "buildings" / "sample.txt", "vanilla")

    vfs = VirtualFilesystem(
        [
            ContentSource("vanilla", SourceKind.VANILLA, vanilla_root, 0),
            ContentSource("my_mod", SourceKind.MOD, mod_root, 100),
        ]
    )

    plan = vfs.plan_write(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings" / "sample.txt",
    )

    assert plan.is_visible is True
    assert plan.current_visible_file is not None
    assert plan.current_visible_file.winner.source.name == "vanilla"
    assert plan.will_override_current_file is True
    assert plan.absolute_path == mod_root / "in_game" / "common" / "buildings" / "sample.txt"


def test_vfs_from_install_loads_replace_rules_from_mod_metadata(tmp_path: Path) -> None:
    install_root = tmp_path / "install"
    game_dir = install_root / "game"
    dlc_dir = game_dir / "dlc"
    mod_dir = game_dir / "mod"
    mod_root = tmp_path / "sample_mod"

    for phase_name in ("loading_screen", "main_menu", "in_game"):
        (game_dir / phase_name).mkdir(parents=True, exist_ok=True)
    dlc_dir.mkdir(parents=True, exist_ok=True)
    mod_dir.mkdir(parents=True, exist_ok=True)

    _write_file(
        mod_root / ".metadata" / "metadata.json",
        '{"name": "Sample Mod", "replace_path": ["game/in_game/common/buildings"]}',
    )

    install = GameInstall(root=install_root, game_dir=game_dir, dlc_dir=dlc_dir, mod_dir=mod_dir)

    vfs = VirtualFilesystem.from_install(install, mod_roots=[mod_root])

    mod_source = vfs.get_source("sample_mod")

    assert mod_source is not None
    assert len(mod_source.replace_rules) == 1
    assert mod_source.replace_rules[0].phase == ContentPhase.IN_GAME
    assert mod_source.replace_rules[0].relative_root == Path("common") / "buildings"
