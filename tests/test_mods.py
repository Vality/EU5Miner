from __future__ import annotations

from pathlib import Path

from eu5miner import apply_mod_update, format_mod_update_report, plan_mod_update
from eu5miner.mods import ModUpdateWriteKind
from eu5miner.source import ContentPhase
from eu5miner.vfs import ContentSource, SourceKind, VirtualFilesystem


def _write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_plan_mod_update_wraps_metadata_and_content_writes(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"
    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])

    update = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "building = {}\n"},
    )

    assert update.metadata_write.kind is ModUpdateWriteKind.METADATA
    assert update.metadata_write.path == mod_root / ".metadata" / "metadata.json"
    assert update.metadata_write.content == "{}\n"
    assert len(update.content_writes) == 1
    assert update.content_writes[0].kind is ModUpdateWriteKind.CONTENT
    assert update.content_writes[0].relative_path == Path("common") / "buildings" / "new.txt"
    assert update.content_writes[0].content == "building = {}\n"
    assert update.replace_paths_to_add == ()
    assert update.blocked_emissions == ()


def test_plan_mod_update_surfaces_replace_path_recommendations(tmp_path: Path) -> None:
    vanilla_root = tmp_path / "vanilla"
    mod_root = tmp_path / "my_mod"

    _write_file(vanilla_root / "in_game" / "common" / "buildings" / "a.txt", "vanilla\n")

    vfs = VirtualFilesystem(
        [
            ContentSource("vanilla", SourceKind.VANILLA, vanilla_root, 0),
            ContentSource("my_mod", SourceKind.MOD, mod_root, 100),
        ]
    )

    update = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "a.txt",),
        content_by_relative_path={"common/buildings/a.txt": "modded\n"},
    )

    assert update.replace_paths_to_add == ("game/in_game/common/buildings",)
    assert update.content_writes[0].relative_path == Path("common") / "buildings" / "a.txt"
    assert update.content_writes[0].content == "modded\n"

    report = format_mod_update_report(update)

    assert "Metadata replace_path additions:" in report
    assert "game/in_game/common/buildings" in report
    assert "override: common/buildings/a.txt" in report


def test_plan_mod_update_surfaces_blocked_emissions(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"
    late_mod_root = tmp_path / "late_mod"

    _write_file(late_mod_root / "in_game" / "common" / "buildings" / "a.txt", "late\n")

    vfs = VirtualFilesystem(
        [
            ContentSource("my_mod", SourceKind.MOD, mod_root, 100),
            ContentSource("late_mod", SourceKind.MOD, late_mod_root, 110),
        ]
    )

    update = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "a.txt",),
    )

    assert len(update.blocked_emissions) == 1
    assert update.blocked_emissions[0].relative_path == Path("common") / "buildings" / "a.txt"
    assert update.blocked_emissions[0].blocker_source_names == ("late_mod",)
    assert update.content_writes == ()

    report = format_mod_update_report(update)

    assert "Blocked emissions:" in report
    assert "common/buildings/a.txt blocked by late_mod" in report


def test_apply_mod_update_materializes_files_and_reports_statuses(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"
    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])

    planned = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "building = {}\n"},
    )

    applied = apply_mod_update(planned)

    assert applied.metadata_write.kind is ModUpdateWriteKind.METADATA
    assert applied.metadata_write.path.read_text(encoding="utf-8") == "{}\n"
    assert len(applied.content_writes) == 1
    assert applied.content_writes[0].path.read_text(encoding="utf-8") == "building = {}\n"

    report = format_mod_update_report(applied)

    assert "Applied mod update: my_mod" in report
    assert "created:" in report
    assert "metadata.json" in report
    assert "new.txt" in report
