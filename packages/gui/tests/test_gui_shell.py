from eu5miner_gui.app import build_placeholder_message
from eu5miner_gui.cli import main


def test_build_placeholder_message_mentions_core_library_phase() -> None:
    message = build_placeholder_message()

    assert "EU5MinerGUI placeholder shell ready." in message
    assert "in_game" in message


def test_cli_main_returns_zero(capsys) -> None:
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "EU5MinerGUI placeholder shell ready." in captured.out
