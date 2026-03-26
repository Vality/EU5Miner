from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.institutions import parse_institution_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_institution_documents(game_install: GameInstall) -> None:
    early = parse_institution_document(
        _read_text(game_install.representative_files()["institution_sample"])
    )
    mid = parse_institution_document(
        _read_text(game_install.representative_files()["institution_secondary_sample"])
    )

    feudalism = early.get_definition("feudalism")
    assert feudalism is not None
    assert feudalism.age == "age_1_traditions"
    assert feudalism.can_spawn is not None
    assert isinstance(feudalism.promote_chance, SemanticObject)
    assert feudalism.spread_from_any_import == "institution_trade_spread_value_early"
    assert feudalism.spread_scale_on_control_if_owner_embraced == "2"

    confessionalism = mid.get_definition("confessionalism")
    assert confessionalism is not None
    assert confessionalism.location == "augsburg"
    assert confessionalism.can_spawn is not None
    assert isinstance(confessionalism.promote_chance, SemanticObject)
    assert confessionalism.spread_from_was_possible_spawn == "institution_spread_from_was_possible_spawn_mid"


def test_institution_parses_inline_variant_fields() -> None:
    document = parse_institution_document(
        "sample_institution = {\n"
        "    age = age_4_reformation\n"
        "    location = rome\n"
        "    can_spawn = { always = yes }\n"
        "    promote_chance = { add = 1 }\n"
        "    spread_from_friendly_coast_border_location = 0.5\n"
        "    spread_from_any_coast_border_location = 0.4\n"
        "    spread_from_any_import = 0.3\n"
        "    spread_from_any_export = 0.2\n"
        "    spread_from_was_possible_spawn = 0.1\n"
        "    spread_scale_on_control_if_owner_embraced = 2\n"
        "    spread_embraced_to_capital = 3\n"
        "    spread_to_market_member = 4\n"
        "    spread = 5\n"
        "}\n"
    )

    definition = document.get_definition("sample_institution")
    assert definition is not None
    assert definition.age == "age_4_reformation"
    assert definition.location == "rome"
    assert definition.can_spawn is not None
    assert isinstance(definition.promote_chance, SemanticObject)
    assert definition.spread_from_any_import == "0.3"
    assert definition.spread == "5"
