from __future__ import annotations

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
