from __future__ import annotations

from pathlib import Path

from eu5miner.cli import main
from eu5miner.source import GameInstall


def test_inspect_install_cli_smoke(game_install: GameInstall, capsys) -> None:
    exit_code = main(["--install-root", str(game_install.root), "inspect-install"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Install root:" in captured.out
    assert "Sources:" in captured.out


def test_list_files_cli_smoke(game_install: GameInstall, capsys) -> None:
    exit_code = main(
        [
            "--install-root",
            str(game_install.root),
            "list-files",
            "--phase",
            "in_game",
            "--subpath",
            "gui",
            "--limit",
            "5",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Merged files for phase=in_game" in captured.out
    assert ".gui" in captured.out


def test_analyze_script_cli_smoke(game_install: GameInstall, capsys) -> None:
    exit_code = main(
        [
            "--install-root",
            str(game_install.root),
            "analyze-script",
            "--representative",
            "scripted_trigger",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "balanced_braces: True" in captured.out
    assert "token_count:" in captured.out


def test_plan_mod_update_cli_reports_dry_run_summary(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")
    mod_root = tmp_path / "my_mod"

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "plan-mod-update",
            "--mod-root",
            str(mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--intended-path",
            "common/buildings/new.txt",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Planned mod update: my_mod" in captured.out
    assert "Summary:" in captured.out
    assert "intended content outputs: 1" in captured.out
    assert captured.err == ""


def test_plan_mod_update_cli_accepts_content_root(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")
    mod_root = tmp_path / "my_mod"
    content_root = tmp_path / "content_root"

    content_file = content_root / "common" / "buildings" / "a.txt"
    content_file.parent.mkdir(parents=True, exist_ok=True)
    content_file.write_text("planned\n", encoding="utf-8")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "plan-mod-update",
            "--mod-root",
            str(mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--content-root",
            str(content_root),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "intended content outputs: 1" in captured.out
    assert "create: common/buildings/a.txt" in captured.out


def test_plan_mod_update_cli_emits_replace_path_notes(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")
    mod_root = tmp_path / "my_mod"
    vanilla_file = install_root / "game" / "in_game" / "common" / "buildings" / "a.txt"
    vanilla_file.parent.mkdir(parents=True, exist_ok=True)
    vanilla_file.write_text("vanilla\n", encoding="utf-8")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "plan-mod-update",
            "--mod-root",
            str(mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--intended-path",
            "common/buildings/a.txt",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Advisories:" in captured.out
    assert "replace_path additions: 1" in captured.out
    assert "note: Planning metadata update to add replace_path entry:" in captured.err


def test_plan_mod_update_cli_emits_shadowing_warnings(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")
    mod_root = tmp_path / "my_mod"
    later_mod_root = tmp_path / "zzz_late_mod"

    later_file = later_mod_root / "in_game" / "common" / "buildings" / "a.txt"
    later_file.parent.mkdir(parents=True, exist_ok=True)
    later_file.write_text("late\n", encoding="utf-8")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "plan-mod-update",
            "--mod-root",
            str(mod_root),
            "--later-mod-root",
            str(later_mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--intended-path",
            "common/buildings/a.txt",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Warnings:" in captured.out
    assert "blocked intended outputs: 1" in captured.out
    assert "warning: Intended output common/buildings/a.txt will be shadowed" in captured.err


def test_apply_mod_update_cli_materializes_content_and_emits_notes(
    tmp_path: Path,
    capsys,
) -> None:
    install_root = _make_test_install(tmp_path / "install")
    mod_root = tmp_path / "my_mod"
    vanilla_file = install_root / "game" / "in_game" / "common" / "buildings" / "a.txt"
    content_file = tmp_path / "payload.txt"

    vanilla_file.parent.mkdir(parents=True, exist_ok=True)
    vanilla_file.write_text("vanilla\n", encoding="utf-8")
    content_file.write_text("modded\n", encoding="utf-8")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "apply-mod-update",
            "--mod-root",
            str(mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--content-file",
            f"common/buildings/a.txt={content_file}",
        ]
    )

    captured = capsys.readouterr()
    written_file = mod_root / "in_game" / "common" / "buildings" / "a.txt"

    assert exit_code == 0
    assert written_file.read_text(encoding="utf-8") == "modded\n"
    assert "Applied mod update: my_mod" in captured.out
    assert "created writes: 2" in captured.out
    assert "Advisories:" in captured.out
    assert "note: Planning metadata update to add replace_path entry:" in captured.err


def test_apply_mod_update_cli_accepts_content_root(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")
    mod_root = tmp_path / "my_mod"
    content_root = tmp_path / "content_root"
    content_file = content_root / "common" / "buildings" / "a.txt"

    content_file.parent.mkdir(parents=True, exist_ok=True)
    content_file.write_text("from root\n", encoding="utf-8")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "apply-mod-update",
            "--mod-root",
            str(mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--content-root",
            str(content_root),
        ]
    )

    captured = capsys.readouterr()
    written_file = mod_root / "in_game" / "common" / "buildings" / "a.txt"

    assert exit_code == 0
    assert written_file.read_text(encoding="utf-8") == "from root\n"
    assert "Applied mod update: my_mod" in captured.out


def test_apply_mod_update_cli_reports_bad_content_mapping(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")
    mod_root = tmp_path / "my_mod"

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "apply-mod-update",
            "--mod-root",
            str(mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--content-file",
            "not-a-valid-mapping",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "error: Content file mappings must use the form" in captured.err


def test_apply_mod_update_cli_requires_some_content_or_intent(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")
    mod_root = tmp_path / "my_mod"

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "apply-mod-update",
            "--mod-root",
            str(mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert (
        "error: At least one --intended-path, --content-file, or --content-root "
        "entry is required"
    ) in captured.err


def test_apply_mod_update_cli_respects_no_overwrite(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")
    mod_root = tmp_path / "my_mod"
    content_file = tmp_path / "payload.txt"
    target_file = mod_root / "in_game" / "common" / "buildings" / "a.txt"

    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("old\n", encoding="utf-8")
    content_file.write_text("new\n", encoding="utf-8")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "apply-mod-update",
            "--mod-root",
            str(mod_root),
            "--phase",
            "in_game",
            "--subtree",
            "common/buildings",
            "--content-file",
            f"common/buildings/a.txt={content_file}",
            "--no-overwrite",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "error: Refusing to overwrite existing file:" in captured.err
    assert target_file.read_text(encoding="utf-8") == "old\n"


def _make_test_install(install_root: Path) -> Path:
    game_dir = install_root / "game"
    for phase_name in ("loading_screen", "main_menu", "in_game"):
        (game_dir / phase_name).mkdir(parents=True, exist_ok=True)
    (game_dir / "dlc").mkdir(parents=True, exist_ok=True)
    (game_dir / "mod").mkdir(parents=True, exist_ok=True)
    return install_root
