from __future__ import annotations

from pathlib import Path

from eu5miner.domains.religious_aspects import parse_religious_aspect_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_real_religious_aspect_document(game_install: GameInstall) -> None:
    document = parse_religious_aspect_document(
        _read_text(game_install.representative_files()["religious_aspect_sample"])
    )

    adoptionism = document.get_definition("adoptionism")
    assert adoptionism is not None
    assert adoptionism.religions == ("bogomilism", "catharism", "lollardy", "paulicianism")
    assert adoptionism.enabled is not None
    assert adoptionism.modifier is not None
    assert adoptionism.opinions[0].aspect == "adoptionism"
    assert adoptionism.opinions[0].score == "10"


def test_religious_aspect_parses_inline_fields() -> None:
    document = parse_religious_aspect_document(
        "sample_aspect = {\n"
        "    religion = catholic\n"
        "    religion = orthodox\n"
        "    visible = { always = yes }\n"
        "    enabled = { always = yes }\n"
        "    modifier = { tolerance_own = 1 }\n"
        "    opinions = { sample_aspect = 10 rival_aspect = -5 }\n"
        "}\n"
    )

    definition = document.get_definition("sample_aspect")
    assert definition is not None
    assert definition.religions == ("catholic", "orthodox")
    assert definition.visible is not None
    assert definition.enabled is not None
    assert definition.modifier is not None
    assert tuple(opinion.aspect for opinion in definition.opinions) == (
        "sample_aspect",
        "rival_aspect",
    )
