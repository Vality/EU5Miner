from __future__ import annotations

from pathlib import Path

from eu5miner_gui.app import build_shell_message
from eu5miner_gui.cli import main


def test_build_shell_message_lists_supported_systems_without_install() -> None:
    message = build_shell_message()

    assert "EU5MinerGUI read-only shell ready." in message
    assert "Supported systems:" in message
    assert "- map:" in message
    assert "Install summary: not loaded." in message


def test_cli_main_returns_zero(capsys) -> None:
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "EU5MinerGUI read-only shell ready." in captured.out
    assert "Supported systems:" in captured.out


def test_cli_selected_system_report_from_synthetic_install(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")

    exit_code = main(["--install-root", str(install_root), "--system", "map"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Install root:" in captured.out
    assert "System report: map" in captured.out
    assert "location hierarchy definitions:" in captured.out


def _make_test_install(install_root: Path) -> Path:
    game_dir = install_root / "game"
    for phase_name in ("loading_screen", "main_menu", "in_game"):
        (game_dir / phase_name).mkdir(parents=True, exist_ok=True)
    (game_dir / "dlc").mkdir(parents=True, exist_ok=True)
    (game_dir / "mod").mkdir(parents=True, exist_ok=True)

    _write_text(
        game_dir / "in_game" / "map_data" / "default.map",
        'definitions = "definitions.txt"\n'
        'adjacencies = "adjacencies.csv"\n'
        'ports = "ports.csv"\n'
        "wrap_x = no\n",
    )
    _write_text(
        game_dir / "in_game" / "map_data" / "definitions.txt",
        "world = {\n"
        "    region = {\n"
        "        area = {\n"
        "            province = { stockholm uppsala }\n"
        "        }\n"
        "    }\n"
        "}\n",
    )
    _write_text(
        game_dir / "in_game" / "map_data" / "adjacencies.csv",
        "From;To;Type;Through;start_x;start_y;stop_x;stop_y;Comment\n"
        "stockholm;uppsala;river;;1;2;3;4;synthetic\n",
    )
    _write_text(
        game_dir / "in_game" / "map_data" / "ports.csv",
        "LandProvince;SeaZone;x;y;\nstockholm;inner_sea;10;20;x\n",
    )
    _write_text(
        game_dir / "main_menu" / "setup" / "start" / "10_countries.txt",
        "countries = {\n"
        "    countries = {\n"
        "        SWE = {\n"
        "            own_control_core = { stockholm uppsala }\n"
        "            capital = stockholm\n"
        "        }\n"
        "    }\n"
        "}\n",
    )
    _write_text(
        game_dir / "main_menu" / "setup" / "start" / "21_locations.txt",
        "locations = {\n"
        "    stockholm = { timed_modifiers = { } }\n"
        "}\n",
    )
    return install_root


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
