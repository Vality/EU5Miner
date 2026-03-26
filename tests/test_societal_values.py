from __future__ import annotations

from pathlib import Path

from eu5miner.domains.societal_values import parse_societal_value_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_real_societal_value_document(game_install: GameInstall) -> None:
    document = parse_societal_value_document(
        _read_text(game_install.representative_files()["societal_value_sample"])
    )

    definition = document.get_definition("spiritualist_vs_humanist")
    assert definition is not None
    assert definition.left_modifier is not None
    assert definition.right_modifier is not None
    assert definition.left_modifier.get_scalar("tolerance_own") == "2"
    assert definition.right_modifier.get_scalar("tolerance_heathen") == "1"
    assert definition.opinion_importance_multiplier is None


def test_societal_value_parses_inline_fields() -> None:
    document = parse_societal_value_document(
        "tradition_vs_change = {\n"
        "    left_modifier = { stability_cost = -0.1 }\n"
        "    right_modifier = { global_max_literacy = 5 }\n"
        "    opinion_importance_multiplier = 0.5\n"
        "}\n"
    )

    definition = document.get_definition("tradition_vs_change")
    assert definition is not None
    assert definition.left_modifier is not None
    assert definition.right_modifier is not None
    assert definition.opinion_importance_multiplier == 0.5