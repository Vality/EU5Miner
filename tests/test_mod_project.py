from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.mod_project import (
    MaterializedWriteStatus,
    ModSkeletonFileKind,
    materialize_targeted_mod_emission,
    plan_mod_skeleton,
    plan_targeted_mod_emission,
)
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


def test_plan_targeted_mod_emission_builds_metadata_and_content_writes(
    tmp_path: Path,
) -> None:
    mod_root = tmp_path / "my_mod"

    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])
    emission_plan = vfs.plan_mod_directory_emission(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
    )

    targeted = plan_targeted_mod_emission(
        emission_plan,
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "building = {}\n"},
    )

    assert targeted.metadata_write.path == mod_root / ".metadata" / "metadata.json"
    assert targeted.metadata_write.content == "{}\n"
    assert len(targeted.content_writes) == 1
    assert targeted.content_writes[0].path == (
        mod_root / "in_game" / "common" / "buildings" / "new.txt"
    )
    assert targeted.content_writes[0].content == "building = {}\n"


def test_plan_targeted_mod_emission_adds_replace_path_to_existing_metadata(
    tmp_path: Path,
) -> None:
    vanilla_root = tmp_path / "vanilla"
    mod_root = tmp_path / "my_mod"

    _write_file(vanilla_root / "in_game" / "common" / "buildings" / "a.txt", "vanilla a")
    _write_file(mod_root / ".metadata" / "metadata.json", '{"name": "My Mod", "replace_path": []}')

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

    targeted = plan_targeted_mod_emission(emission_plan)

    assert '"name": "My Mod"' in targeted.metadata_write.content
    assert '"replace_path": [' in targeted.metadata_write.content
    assert '"game/in_game/common/buildings"' in targeted.metadata_write.content


def test_plan_targeted_mod_emission_deduplicates_existing_replace_path(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"

    _write_file(
        mod_root / ".metadata" / "metadata.json",
        '{"replace_path": ["game/in_game/common/buildings"]}',
    )
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

    targeted = plan_targeted_mod_emission(emission_plan)

    assert targeted.metadata_write.content.count('"game/in_game/common/buildings"') == 1


def test_plan_targeted_mod_emission_keeps_blocked_outputs_out_of_content_writes(
    tmp_path: Path,
) -> None:
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

    targeted = plan_targeted_mod_emission(emission_plan)

    assert targeted.content_writes == ()
    assert len(targeted.blocked_emissions) == 1


def test_materialize_targeted_mod_emission_creates_directories_and_files(
    tmp_path: Path,
) -> None:
    mod_root = tmp_path / "my_mod"

    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])
    emission_plan = vfs.plan_mod_directory_emission(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
    )
    targeted = plan_targeted_mod_emission(
        emission_plan,
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "building = {}\n"},
    )

    materialized = materialize_targeted_mod_emission(targeted)

    assert mod_root / ".metadata" in materialized.created_directories
    assert materialized.metadata_write.status is MaterializedWriteStatus.CREATED
    assert materialized.metadata_write.path.read_text(encoding="utf-8") == "{}\n"
    assert len(materialized.content_writes) == 1
    assert materialized.content_writes[0].status is MaterializedWriteStatus.CREATED
    assert materialized.content_writes[0].path.read_text(encoding="utf-8") == "building = {}\n"


def test_materialize_targeted_mod_emission_marks_identical_existing_files_unchanged(
    tmp_path: Path,
) -> None:
    mod_root = tmp_path / "my_mod"

    _write_file(mod_root / ".metadata" / "metadata.json", "{}\n")
    _write_file(mod_root / "in_game" / "common" / "buildings" / "new.txt", "building = {}\n")

    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])
    emission_plan = vfs.plan_mod_directory_emission(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
    )
    targeted = plan_targeted_mod_emission(
        emission_plan,
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "building = {}\n"},
    )

    materialized = materialize_targeted_mod_emission(targeted, overwrite=False)

    assert materialized.metadata_write.status is MaterializedWriteStatus.UNCHANGED
    assert materialized.content_writes[0].status is MaterializedWriteStatus.UNCHANGED


def test_materialize_targeted_mod_emission_rejects_overwrite_when_disabled(
    tmp_path: Path,
) -> None:
    mod_root = tmp_path / "my_mod"

    _write_file(mod_root / ".metadata" / "metadata.json", "{}\n")
    _write_file(mod_root / "in_game" / "common" / "buildings" / "new.txt", "old\n")

    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])
    emission_plan = vfs.plan_mod_directory_emission(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
    )
    targeted = plan_targeted_mod_emission(
        emission_plan,
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "building = {}\n"},
    )

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        materialize_targeted_mod_emission(targeted, overwrite=False)


def test_materialize_targeted_mod_emission_updates_existing_file_when_enabled(
    tmp_path: Path,
) -> None:
    mod_root = tmp_path / "my_mod"

    _write_file(mod_root / "in_game" / "common" / "buildings" / "new.txt", "old\n")

    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])
    emission_plan = vfs.plan_mod_directory_emission(
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
    )
    targeted = plan_targeted_mod_emission(
        emission_plan,
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "building = {}\n"},
    )

    materialized = materialize_targeted_mod_emission(targeted, overwrite=True)

    assert materialized.content_writes[0].status is MaterializedWriteStatus.UPDATED
    assert materialized.content_writes[0].path.read_text(encoding="utf-8") == "building = {}\n"
