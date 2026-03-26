from __future__ import annotations

from pathlib import Path

from eu5miner.domains.religious_figures import parse_religious_figure_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_parse_real_religious_figure_documents(game_install: GameInstall) -> None:
    muslim = parse_religious_figure_document(
        _read_text(game_install.representative_files()["religious_figure_sample"])
    )
    hindu = parse_religious_figure_document(
        _read_text(game_install.representative_files()["religious_figure_secondary_sample"])
    )

    scholar = muslim.get_definition("muslim_scholar")
    assert scholar is not None
    assert scholar.enabled_for_religion is not None
    assert scholar.enabled_for_religion.get_scalar("group") == "religion_group:muslim"

    guru = hindu.get_definition("guru")
    assert guru is not None
    assert guru.enabled_for_religion is not None
    assert guru.enabled_for_religion.get_scalar("this.group") == "religion_group:dharmic"


def test_religious_figure_parses_inline_fields() -> None:
    document = parse_religious_figure_document(
        "sample_figure = { enabled_for_religion = { group = religion_group:christian } }\n"
    )

    definition = document.get_definition("sample_figure")
    assert definition is not None
    assert definition.enabled_for_religion is not None
    assert definition.enabled_for_religion.get_scalar("group") == "religion_group:christian"