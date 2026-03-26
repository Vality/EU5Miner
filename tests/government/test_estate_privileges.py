from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.government.estate_privileges import parse_estate_privilege_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_estate_privilege_documents(game_install: GameInstall) -> None:
    burghers = parse_estate_privilege_document(
        _read_text(game_install.representative_files()["estate_privilege_sample"])
    )
    clergy = parse_estate_privilege_document(
        _read_text(game_install.representative_files()["estate_privilege_secondary_sample"])
    )
    nobles = parse_estate_privilege_document(
        _read_text(game_install.representative_files()["estate_privilege_special_sample"])
    )

    formal_guilds = burghers.get_definition("formal_guilds")
    assert formal_guilds is not None
    assert formal_guilds.estate == "burghers_estate"
    assert len(formal_guilds.country_modifiers) == 1
    assert formal_guilds.potential is None
    assert formal_guilds.allow is None

    novgorod = burghers.get_definition("novgorod_ivans_hundred")
    assert novgorod is not None
    assert len(novgorod.country_modifiers) == 3
    assert novgorod.can_revoke is not None

    enforced_unity = clergy.get_definition("clergy_enforced_unity")
    assert enforced_unity is not None
    assert enforced_unity.estate == "clergy_estate"
    assert enforced_unity.potential is not None
    assert enforced_unity.allow is not None
    assert enforced_unity.can_revoke is not None
    assert enforced_unity.months == 3

    apostolic_tax = clergy.get_definition("apostolic_tax_privilege")
    assert apostolic_tax is not None
    assert apostolic_tax.on_activate is not None
    assert apostolic_tax.on_deactivate is not None

    liberum_veto = nobles.get_definition("liberum_veto")
    assert liberum_veto is not None
    assert liberum_veto.can_revoke is not None
    assert liberum_veto.on_activate is not None

    powerful_families = nobles.get_definition("powerful_italian_families")
    assert powerful_families is not None
    assert len(powerful_families.location_modifiers) == 1
    assert len(powerful_families.country_modifiers) == 1


def test_estate_privilege_parses_inline_variant_fields() -> None:
    document = parse_estate_privilege_document(
        "sample_privilege = {\n"
        "    estate = nobles_estate\n"
        "    potential = { always = yes }\n"
        "    allow = { always = yes }\n"
        "    can_revoke = { always = no }\n"
        "    on_activate = { add = 1 }\n"
        "    on_fully_activated = { add = 2 }\n"
        "    on_deactivate = { add = 3 }\n"
        "    country_modifier = { tax = 1 }\n"
        "    country_modifier = { prestige = 1 }\n"
        "    province_modifier = { dev = 1 }\n"
        "    location_modifier = { attr = 1 }\n"
        "    years = 2\n"
        "    months = 3\n"
        "    weeks = 4\n"
        "    days = 5\n"
        "}\n"
    )

    definition = document.get_definition("sample_privilege")
    assert definition is not None
    assert definition.estate == "nobles_estate"
    assert definition.potential is not None
    assert definition.allow is not None
    assert definition.can_revoke is not None
    assert definition.on_activate is not None
    assert definition.on_fully_activated is not None
    assert definition.on_deactivate is not None
    assert len(definition.country_modifiers) == 2
    assert len(definition.province_modifiers) == 1
    assert len(definition.location_modifiers) == 1
    assert definition.years == 2
    assert definition.months == 3
    assert definition.weeks == 4
    assert definition.days == 5
