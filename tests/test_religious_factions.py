from __future__ import annotations

from pathlib import Path

from eu5miner.domains.religious_factions import parse_religious_faction_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_real_religious_faction_document(game_install: GameInstall) -> None:
    document = parse_religious_faction_document(
        _read_text(game_install.representative_files()["religious_faction_sample"])
    )

    faction = document.get_definition("imperial_court")
    assert faction is not None
    assert faction.visible is not None
    assert faction.enabled is not None
    assert faction.actions == (
        "get_claim_from_imperial_court",
        "get_marriage_from_imperial_court",
        "become_shogun_from_imperial_court",
    )


def test_religious_faction_parses_inline_fields() -> None:
    document = parse_religious_faction_document(
        "sample_faction = {\n"
        "    visible = { always = yes }\n"
        "    enabled = { has_ruler = yes }\n"
        "    actions = { action_a action_b }\n"
        "}\n"
    )

    definition = document.get_definition("sample_faction")
    assert definition is not None
    assert definition.visible is not None
    assert definition.enabled is not None
    assert definition.actions == ("action_a", "action_b")