from __future__ import annotations

from pathlib import Path

from eu5miner.domains.holy_site_types import parse_holy_site_type_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_real_holy_site_type_document(game_install: GameInstall) -> None:
    document = parse_holy_site_type_document(
        _read_text(game_install.representative_files()["holy_site_type_sample"])
    )

    shrine = document.get_definition("shrine")
    assert shrine is not None
    assert shrine.location_modifier is not None
    assert shrine.country_modifier is None

    christian = document.get_definition("christian_holy_site")
    assert christian is not None
    assert christian.location_modifier is not None
    assert christian.country_modifier is not None


def test_holy_site_type_parses_inline_variant_fields() -> None:
    document = parse_holy_site_type_document(
        "sample_type = {\n"
        "    country_modifier = { add = 1 }\n"
        "    location_modifier = { add = 2 }\n"
        "    religion_modifier = { add = 3 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_type")
    assert definition is not None
    assert definition.country_modifier is not None
    assert definition.location_modifier is not None
    assert definition.religion_modifier is not None
