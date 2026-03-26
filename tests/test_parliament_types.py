from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.parliament_types import parse_parliament_type_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_parliament_type_documents(game_install: GameInstall) -> None:
    country_document = parse_parliament_type_document(
        _read_text(game_install.representative_files()["parliament_type_sample"])
    )
    io_document = parse_parliament_type_document(
        _read_text(game_install.representative_files()["parliament_type_secondary_sample"])
    )

    assembly = country_document.get_definition("assembly")
    assert assembly is not None
    assert assembly.parliament_type == "country"
    assert assembly.allow is not None
    assert assembly.modifier is not None

    estate_parliament = country_document.get_definition("estate_parliament")
    assert estate_parliament is not None
    assert estate_parliament.potential is not None
    assert estate_parliament.allow is not None

    union_assembly = io_document.get_definition("union_royal_assembly")
    assert union_assembly is not None
    assert union_assembly.parliament_type == "international_organization"
    assert union_assembly.potential is not None
    assert union_assembly.locked is not None
    assert union_assembly.modifier is not None


def test_parliament_type_parses_inline_variant_fields() -> None:
    document = parse_parliament_type_document(
        "sample_parliament = {\n"
        "    type = country\n"
        "    potential = { always = yes }\n"
        "    allow = { always = yes }\n"
        "    locked = { always = no }\n"
        "    modifier = { add = 1 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_parliament")
    assert definition is not None
    assert definition.parliament_type == "country"
    assert definition.potential is not None
    assert definition.allow is not None
    assert definition.locked is not None
    assert definition.modifier is not None
