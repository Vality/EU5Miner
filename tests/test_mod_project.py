from __future__ import annotations

from pathlib import Path

from eu5miner.domains.mod_project import ModSkeletonFileKind, plan_mod_skeleton
from eu5miner.source import ContentPhase
from eu5miner.vfs import ContentSource, ReplacePathRule, SourceKind, VirtualFilesystem


def _write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_plan_mod_skeleton_includes_metadata_and_content_layout(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"

    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])
    emission_plan = vfs.plan_mod_directory_emission(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
    )

    skeleton = plan_mod_skeleton(emission_plan)

    assert skeleton.root == mod_root
    assert mod_root in skeleton.directories
    assert mod_root / ".metadata" in skeleton.directories
    assert mod_root / "in_game" / "common" / "buildings" in skeleton.directories
    assert skeleton.metadata_file.path == mod_root / ".metadata" / "metadata.json"
    assert skeleton.metadata_file.kind is ModSkeletonFileKind.METADATA
    assert len(skeleton.content_files) == 1
    assert skeleton.content_files[0].path == (
        mod_root / "in_game" / "common" / "buildings" / "new.txt"
    )
    assert skeleton.blocked_emissions == ()


def test_plan_mod_skeleton_preserves_metadata_update_count(tmp_path: Path) -> None:
    vanilla_root = tmp_path / "vanilla"
    mod_root = tmp_path / "my_mod"

    _write_file(vanilla_root / "in_game" / "common" / "buildings" / "a.txt", "vanilla a")

    vfs = VirtualFilesystem(
        [
            ContentSource("vanilla", SourceKind.VANILLA, vanilla_root, 0),
            ContentSource("my_mod", SourceKind.MOD, mod_root, 100),
        ]
    )
    emission_plan = vfs.plan_mod_directory_emission(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "a.txt",),
    )

    skeleton = plan_mod_skeleton(emission_plan)

    assert skeleton.metadata_update_actions_count == 1
    assert len(skeleton.content_files) == 1
    assert skeleton.content_files[0].exists is False


def test_plan_mod_skeleton_separates_blocked_intended_outputs(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"
    late_mod_root = tmp_path / "late_mod"

    _write_file(late_mod_root / "in_game" / "common" / "buildings" / "a.txt", "late mod a")

    vfs = VirtualFilesystem(
        [
            ContentSource("my_mod", SourceKind.MOD, mod_root, 100),
            ContentSource("late_mod", SourceKind.MOD, late_mod_root, 110),
        ]
    )
    emission_plan = vfs.plan_mod_directory_emission(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "a.txt",),
    )

    skeleton = plan_mod_skeleton(emission_plan)

    assert len(skeleton.content_files) == 0
    assert len(skeleton.blocked_emissions) == 1
    assert skeleton.blocked_emissions[0].relative_path == Path("common") / "buildings" / "a.txt"


def test_plan_mod_skeleton_marks_existing_content_file(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"

    _write_file(mod_root / ".metadata" / "metadata.json", "{}")
    _write_file(mod_root / "in_game" / "common" / "buildings" / "owned.txt", "owned")

    vfs = VirtualFilesystem(
        [
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
            )
        ]
    )
    emission_plan = vfs.plan_mod_directory_emission(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "owned.txt",),
    )

    skeleton = plan_mod_skeleton(emission_plan)

    assert skeleton.metadata_file.exists is True
    assert len(skeleton.content_files) == 1
    assert skeleton.content_files[0].exists is True
