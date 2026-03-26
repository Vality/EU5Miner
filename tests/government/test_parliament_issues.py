from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.government.parliament_issues import parse_parliament_issue_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_parliament_issue_documents(game_install: GameInstall) -> None:
    country_document = parse_parliament_issue_document(
        _read_text(game_install.representative_files()["parliament_issue_sample"])
    )
    io_document = parse_parliament_issue_document(
        _read_text(game_install.representative_files()["parliament_issue_special_sample"])
    )

    bolster_monarchy = country_document.get_definition("bolster_the_monarchy")
    assert bolster_monarchy is not None
    assert bolster_monarchy.issue_type is None
    assert bolster_monarchy.estates == ("crown_estate",)
    assert bolster_monarchy.modifier_when_in_debate is not None
    assert bolster_monarchy.allow is not None
    assert isinstance(bolster_monarchy.chance, SemanticObject)
    assert bolster_monarchy.on_debate_passed is not None
    assert bolster_monarchy.on_debate_failed is not None

    law_debate = io_document.get_definition("hre_law_debate")
    assert law_debate is not None
    assert law_debate.issue_type == "international_organization"
    assert law_debate.show_message is False
    assert law_debate.special_statuses == ("emperor",)
    assert law_debate.potential is not None
    assert law_debate.allow is not None
    assert law_debate.chance == "0"
    assert law_debate.on_debate_passed is not None
    assert law_debate.on_debate_failed is not None
    assert law_debate.wants_this_parliament_issue_bias is not None

    military_support = io_document.get_definition("hre_request_additional_military_support")
    assert military_support is not None
    assert military_support.selectable_for is not None


def test_parliament_issue_parses_inline_variant_fields() -> None:
    document = parse_parliament_issue_document(
        "sample_issue = {\n"
        "    type = international_organization\n"
        "    estate = crown_estate\n"
        "    special_status = emperor\n"
        "    show_message = no\n"
        "    modifier_when_in_debate = { add = 1 }\n"
        "    allow = { always = yes }\n"
        "    potential = { always = yes }\n"
        "    selectable_for = { always = yes }\n"
        "    chance = { add = 2 }\n"
        "    on_debate_passed = { add = 3 }\n"
        "    on_debate_failed = { add = 4 }\n"
        "    on_debate_start = { add = 5 }\n"
        "    wants_this_parliament_issue_bias = { add = 6 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_issue")
    assert definition is not None
    assert definition.issue_type == "international_organization"
    assert definition.estates == ("crown_estate",)
    assert definition.special_statuses == ("emperor",)
    assert definition.show_message is False
    assert definition.modifier_when_in_debate is not None
    assert definition.allow is not None
    assert definition.potential is not None
    assert definition.selectable_for is not None
    assert isinstance(definition.chance, SemanticObject)
    assert definition.on_debate_passed is not None
    assert definition.on_debate_failed is not None
    assert definition.on_debate_start is not None
    assert definition.wants_this_parliament_issue_bias is not None
