from __future__ import annotations

from pathlib import Path

from eu5miner.formats.script_text import analyze_script_text
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_script_analysis_detects_expected_constructs(game_install: GameInstall) -> None:
    text = _read_text(game_install.representative_files()["scripted_trigger"])
    features = analyze_script_text(text)

    assert features.balanced_braces
    assert features.comment_lines >= 1
    assert features.macro_count >= 1
    assert features.scoped_reference_count >= 1
    assert features.typed_reference_count >= 1


def test_gui_sample_has_balanced_structure(game_install: GameInstall) -> None:
    text = _read_text(game_install.representative_files()["gui_sample"])
    features = analyze_script_text(text)

    assert features.balanced_braces
    assert features.gui_expression_count >= 1


def test_inline_entry_mode_detection() -> None:
    text = "INJECT:sample = { value = 1 }\nREPLACE:test = { another = yes }\n"
    features = analyze_script_text(text)

    assert features.balanced_braces
    assert features.entry_mode_count == 2
