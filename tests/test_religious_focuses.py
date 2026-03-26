from __future__ import annotations

from pathlib import Path

from eu5miner.domains.religious_focuses import parse_religious_focus_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_real_religious_focus_document(game_install: GameInstall) -> None:
    document = parse_religious_focus_document(
        _read_text(game_install.representative_files()["religious_focus_sample"])
    )

    focus = document.get_definition("adopt_ometeotl")
    assert focus is not None
    assert focus.monthly_progress is not None
    assert focus.allow is not None
    assert focus.modifier_while_progressing is not None
    assert focus.modifier_on_completion is not None
    assert focus.ai_will_do is not None


def test_religious_focus_parses_inline_fields() -> None:
    document = parse_religious_focus_document(
        "sample_focus = {\n"
        "    potential = { always = yes }\n"
        "    allow = { has_ruler = yes }\n"
        "    monthly_progress = { add = 1 }\n"
        "    modifier_while_progressing = { tolerance_own = -1 }\n"
        "    modifier_on_completion = { tolerance_own = 1 }\n"
        "    effect_on_completion = { add_stability = 1 }\n"
        "    ai_will_do = { add = 1 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_focus")
    assert definition is not None
    assert definition.potential is not None
    assert definition.allow is not None
    assert definition.monthly_progress is not None
    assert definition.modifier_while_progressing is not None
    assert definition.modifier_on_completion is not None
    assert definition.effect_on_completion is not None
    assert definition.ai_will_do is not None
