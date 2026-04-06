from __future__ import annotations

from pathlib import Path

from eu5miner.cli import main
from tests.integration_support import SyntheticModWorkflowSurface


def _assert_mod_workflow_output_channels(stdout: str, stderr: str) -> None:
    assert "Summary:" in stdout
    assert "Advisories:" in stdout
    assert "Warnings:" in stdout
    assert "note:" not in stdout
    assert "warning:" not in stdout
    assert "Summary:" not in stderr
    assert "Advisories:" not in stderr
    assert "Warnings:" not in stderr


def test_plan_mod_update_cli_contract_combines_content_root_and_intended_paths(
    synthetic_mod_workflow_surface: SyntheticModWorkflowSurface,
    capsys,
) -> None:
    surface = synthetic_mod_workflow_surface
    intended_only_path = Path("common") / "buildings" / "planned_only.txt"

    exit_code = main(
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
            "--intended-path",
            intended_only_path.as_posix(),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Planned mod update: my_mod" in captured.out
    assert "- intended content outputs: 3" in captured.out
    assert "- materialized writes: 3" in captured.out
    assert "- replace_path additions: 1" in captured.out
    assert "- blocked intended outputs: 1" in captured.out
    assert "- override: common/buildings/a.txt" in captured.out
    assert "- create: common/buildings/planned_only.txt" in captured.out
    assert "Planning metadata update to add replace_path entry:" in captured.out
    assert "Intended output common/buildings/blocked.txt will be shadowed" in captured.out
    assert "note: Planning metadata update to add replace_path entry:" in captured.err
    assert "warning: Intended output common/buildings/blocked.txt will be shadowed" in (
        captured.err
    )
    _assert_mod_workflow_output_channels(captured.out, captured.err)


def test_apply_mod_update_cli_contract_combines_all_content_inputs(
    synthetic_mod_workflow_surface: SyntheticModWorkflowSurface,
    tmp_path: Path,
    capsys,
) -> None:
    surface = synthetic_mod_workflow_surface
    intended_only_path = Path("common") / "buildings" / "planned_only.txt"
    mapped_relative_path = Path("common") / "buildings" / "mapped.txt"
    mapped_source = tmp_path / "mapped.txt"
    mapped_source.write_text("mapped = yes\n", encoding="utf-8")

    exit_code = main(
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
            "--content-file",
            f"{mapped_relative_path.as_posix()}={mapped_source}",
            "--intended-path",
            intended_only_path.as_posix(),
        ]
    )

    captured = capsys.readouterr()
    override_file = surface.target_mod_root / "in_game" / surface.override_relative_path
    mapped_file = surface.target_mod_root / "in_game" / mapped_relative_path
    intended_only_file = surface.target_mod_root / "in_game" / intended_only_path
    blocked_file = surface.target_mod_root / "in_game" / surface.blocked_relative_path

    assert exit_code == 0
    assert override_file.read_text(encoding="utf-8") == "override = yes\n"
    assert mapped_file.read_text(encoding="utf-8") == "mapped = yes\n"
    assert intended_only_file.read_text(encoding="utf-8") == ""
    assert blocked_file.exists() is False
    assert "Applied mod update: my_mod" in captured.out
    assert "- created writes: 4" in captured.out
    assert "- blocked intended outputs: 1" in captured.out
    assert "created: " in captured.out
    assert surface.override_relative_path.as_posix() in captured.out
    assert mapped_relative_path.as_posix() in captured.out
    assert intended_only_path.as_posix() in captured.out
    assert "Planning metadata update to add replace_path entry:" in captured.out
    assert "Intended output common/buildings/blocked.txt will be shadowed" in captured.out
    assert "note: Planning metadata update to add replace_path entry:" in captured.err
    assert "warning: Intended output common/buildings/blocked.txt will be shadowed" in (
        captured.err
    )
    _assert_mod_workflow_output_channels(captured.out, captured.err)
