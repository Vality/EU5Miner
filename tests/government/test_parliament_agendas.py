from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.government.parliament_agendas import parse_parliament_agenda_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_parliament_agenda_documents(game_install: GameInstall) -> None:
    country_document = parse_parliament_agenda_document(
        _read_text(game_install.representative_files()["parliament_agenda_sample"])
    )
    io_document = parse_parliament_agenda_document(
        _read_text(game_install.representative_files()["parliament_agenda_special_sample"])
    )

    add_privilege = country_document.get_definition("pa_add_privilege")
    assert add_privilege is not None
    assert add_privilege.agenda_type == "country"
    assert add_privilege.estates == (
        "nobles_estate",
        "clergy_estate",
        "burghers_estate",
        "peasants_estate",
    )
    assert add_privilege.importance == "1.5"
    assert add_privilege.potential is not None
    assert add_privilege.on_accept is not None
    assert add_privilege.can_bribe is not None
    assert add_privilege.on_bribe is not None
    assert add_privilege.ai_will_do is not None
    assert add_privilege.chance == "10"

    lessen_tax = io_document.get_definition("pa_hre_lessen_tax_burden")
    assert lessen_tax is not None
    assert lessen_tax.agenda_type == "international_organization"
    assert lessen_tax.special_statuses == (
        "imperial_prince",
        "free_city",
        "imperial_prelate",
    )
    assert lessen_tax.allow is not None
    assert lessen_tax.on_accept is not None
    assert lessen_tax.ai_will_do is not None


def test_parliament_agenda_parses_inline_variant_fields() -> None:
    document = parse_parliament_agenda_document(
        "sample_agenda = {\n"
        "    type = international_organization\n"
        "    estate = nobles_estate\n"
        "    estate = clergy_estate\n"
        "    special_status = elector\n"
        "    special_status = free_city\n"
        "    potential = { always = yes }\n"
        "    allow = { always = yes }\n"
        "    on_accept = { add = 1 }\n"
        "    on_bribe = { add = 2 }\n"
        "    can_bribe = { always = yes }\n"
        "    ai_will_do = { add = 3 }\n"
        "    chance = { add = 4 }\n"
        "    importance = 5\n"
        "}\n"
    )

    definition = document.get_definition("sample_agenda")
    assert definition is not None
    assert definition.agenda_type == "international_organization"
    assert definition.estates == ("nobles_estate", "clergy_estate")
    assert definition.special_statuses == ("elector", "free_city")
    assert definition.potential is not None
    assert definition.allow is not None
    assert definition.on_accept is not None
    assert definition.on_bribe is not None
    assert definition.can_bribe is not None
    assert definition.ai_will_do is not None
    assert isinstance(definition.chance, SemanticObject)
    assert definition.importance == "5"
