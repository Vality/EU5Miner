from __future__ import annotations

from eu5miner.__main__ import main


def test_package_main_runs_cli_surface(capsys) -> None:
    exit_code = main(["list-systems"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Supported system reports:" in captured.out
    assert "economy" in captured.out