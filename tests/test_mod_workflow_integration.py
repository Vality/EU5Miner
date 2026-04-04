from __future__ import annotations

from pathlib import Path

from eu5miner import apply_mod_update, plan_mod_update
from eu5miner.cli import main
from eu5miner.mods import ModUpdateAdvisoryKind, ModUpdateWarningKind
from eu5miner.source import ContentPhase
from eu5miner.vfs import VirtualFilesystem
from tests.integration_support import SyntheticModWorkflowSurface


def test_library_mod_workflow_integration_surface(
    synthetic_mod_workflow_surface: SyntheticModWorkflowSurface,
) -> None:
    surface = synthetic_mod_workflow_surface
    vfs = VirtualFilesystem.from_install(
        surface.install,
        mod_roots=[surface.target_mod_root, surface.later_mod_root],
    )

    update = plan_mod_update(
        vfs,
        surface.target_mod_root.name,
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(surface.override_relative_path, surface.blocked_relative_path),
        content_by_relative_path={
            surface.override_relative_path: (
                surface.content_root / surface.override_relative_path
            ).read_text(encoding="utf-8"),
            surface.blocked_relative_path: (
                surface.content_root / surface.blocked_relative_path
            ).read_text(encoding="utf-8"),
        },
    )

    assert update.replace_paths_to_add == ("game/in_game/common/buildings",)
    assert len(update.advisories) == 1
    assert update.advisories[0].kind is ModUpdateAdvisoryKind.ADD_REPLACE_PATH
    assert len(update.warnings) == 1
    assert update.warnings[0].kind is ModUpdateWarningKind.BLOCKED_EMISSION
    assert [write.relative_path for write in update.content_writes] == [
        surface.override_relative_path,
    ]

    applied = apply_mod_update(update)

    metadata_path = surface.target_mod_root / ".metadata" / "metadata.json"
    written_file = surface.target_mod_root / "in_game" / surface.override_relative_path
    blocked_file = surface.target_mod_root / "in_game" / surface.blocked_relative_path

    assert metadata_path.read_text(encoding="utf-8") == (
        '{\n  "replace_path": [\n    "game/in_game/common/buildings"\n  ]\n}\n'
    )
    assert written_file.read_text(encoding="utf-8") == "override = yes\n"
    assert blocked_file.exists() is False
    assert applied.warnings == update.warnings
    assert applied.advisories == update.advisories


def test_cli_mod_workflow_integration_surface(
    synthetic_mod_workflow_surface: SyntheticModWorkflowSurface,
    capsys,
) -> None:
    surface = synthetic_mod_workflow_surface

    plan_exit_code = main(
        [
            "--install-root",
            str(surface.install_root),
            "plan-mod-update",
            "--mod-root",
            str(surface.target_mod_root),
            "--later-mod-root",
            str(surface.later_mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--content-root",
            str(surface.content_root),
        ]
    )

    plan_captured = capsys.readouterr()

    assert plan_exit_code == 0
    assert "Advisories:" in plan_captured.out
    assert "Warnings:" in plan_captured.out
    assert "note: Planning metadata update to add replace_path entry:" in plan_captured.err
    assert (
        "warning: Intended output common/buildings/blocked.txt will be shadowed"
    ) in plan_captured.err

    apply_exit_code = main(
        [
            "--install-root",
            str(surface.install_root),
            "apply-mod-update",
            "--mod-root",
            str(surface.target_mod_root),
            "--later-mod-root",
            str(surface.later_mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--content-root",
            str(surface.content_root),
        ]
    )

    apply_captured = capsys.readouterr()
    written_file = surface.target_mod_root / "in_game" / surface.override_relative_path
    blocked_file = surface.target_mod_root / "in_game" / surface.blocked_relative_path

    assert apply_exit_code == 0
    assert "Applied mod update: my_mod" in apply_captured.out
    assert written_file.read_text(encoding="utf-8") == "override = yes\n"
    assert blocked_file.exists() is False
