from __future__ import annotations

from pathlib import Path

from eu5miner_gui.__main__ import main as package_main
from eu5miner_gui.app import build_shell_message
from eu5miner_gui.browser import build_browser_model
from eu5miner_gui.cli import main


def test_build_shell_message_lists_supported_systems_without_install() -> None:
    message = build_shell_message()

    assert "EU5MinerGUI read-only browser ready." in message
    assert "Available pages:" in message
    assert "== Install overview ==" in message
    assert "Supported systems:" in message
    assert "- map: Map text, map CSV, and linked setup-location coverage." in message
    assert "Install summary:" in message
    assert "- Not loaded." in message


def test_build_browser_model_with_selected_system_builds_overview_and_report_pages(
    tmp_path: Path,
) -> None:
    install_root = _make_test_install(tmp_path / "install")

    model = build_browser_model(install_root, selected_system="map")

    assert model.selected_page_key == "map"
    assert model.page_keys() == ("overview", "map")
    assert model.pages[1].title == "map system report"
    assert model.pages[1].status == "ready"
    assert model.pages[1].sections[1].lines[0] == "default.map referenced files: 2"
    assert any(
        line.startswith("location hierarchy definitions:")
        for line in model.pages[1].sections[1].lines
    )


def test_build_browser_model_with_all_systems_loads_all_report_pages(tmp_path: Path) -> None:
    install_root = _make_test_install(tmp_path / "install")

    model = build_browser_model(install_root, include_all_systems=True)

    assert model.selected_page_key == "overview"
    assert model.page_keys() == (
        "overview",
        "economy",
        "diplomacy",
        "government",
        "religion",
        "interface",
        "map",
    )
    assert model.pages[0].sections[0].lines[2] == "Ready report pages: map"
    assert model.pages[0].sections[0].lines[3] == (
        "Unavailable report pages: economy, diplomacy, government, religion, interface"
    )
    assert model.pages[1].status == "unavailable"
    assert model.pages[-1].status == "ready"


def test_cli_main_returns_zero(capsys) -> None:
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "EU5MinerGUI read-only browser ready." in captured.out
    assert "Available pages:" in captured.out


def test_package_main_returns_zero(capsys) -> None:
    assert package_main([]) == 0
    captured = capsys.readouterr()
    assert "EU5MinerGUI read-only browser ready." in captured.out
    assert "Available pages:" in captured.out


def test_cli_selected_system_report_from_synthetic_install(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")

    exit_code = main(["--install-root", str(install_root), "--system", "map"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Selected page: map" in captured.out
    assert "== map system report ==" in captured.out
    assert "Representative files:" in captured.out
    assert "- map_default" in captured.out
    assert "- default.map referenced files: 2" in captured.out
    assert "- location hierarchy definitions: 2" in captured.out


def test_cli_all_systems_from_synthetic_install(tmp_path: Path, capsys) -> None:
    install_root = _make_test_install(tmp_path / "install")

    exit_code = main(["--install-root", str(install_root), "--all-systems"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Selected page: overview" in captured.out
    assert "- economy: economy system report (unavailable)" in captured.out
    assert "- map: map system report" in captured.out
    assert "== economy system report ==" in captured.out
    assert "- Unavailable from selected install." in captured.out
    assert "== diplomacy system report ==" in captured.out
    assert "== government system report ==" in captured.out
    assert "== religion system report ==" in captured.out
    assert "== interface system report ==" in captured.out
    assert "== map system report ==" in captured.out


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
