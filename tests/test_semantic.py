from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.formats.semantic import SemanticObject, SemanticScalar, parse_semantic_document
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_semantic_document_exposes_scripted_trigger_object(game_install: GameInstall) -> None:
    document = parse_semantic_document(
        _read_text(game_install.representative_files()["scripted_trigger"])
    )

    first_entry = document.entries[0]
    assert first_entry.key == "country_can_ennoble_trigger"
    assert first_entry.operator == "="
    assert isinstance(first_entry.value, SemanticObject)
    assert first_entry.value.first_entry("OR") is not None


@pytest.mark.timeout(5)
def test_semantic_document_exposes_setup_country_data(game_install: GameInstall) -> None:
    document = parse_semantic_document(
        _read_text(game_install.representative_files()["setup_country_sample"])
    )

    france = document.first_entry("FRA")
    assert france is not None
    assert isinstance(france.value, SemanticObject)
    assert france.value.get_scalar("culture_definition") == "french"
    assert france.value.get_scalar("difficulty") == "3"


def test_semantic_document_supports_inline_object_helpers() -> None:
    document = parse_semantic_document(
        "FRA = {\n"
        "    difficulty = 3\n"
        "    religion_definition = catholic\n"
        "    color = rgb { 16 41 202 }\n"
        "}\n"
    )

    france = document.first_entry("FRA")
    assert france is not None
    assert isinstance(france.value, SemanticObject)
    assert france.value.get_scalar("difficulty") == "3"
    assert france.value.get_scalar("religion_definition") == "catholic"

    color = france.value.first_entry("color")
    assert color is not None
    assert isinstance(color.value, SemanticObject)
    assert color.value.prefix == "rgb"


def test_semantic_document_supports_inline_scalars() -> None:
    document = parse_semantic_document("prestige > 70\n")

    entry = document.entries[0]
    assert entry.key == "prestige"
    assert entry.operator == ">"
    assert isinstance(entry.value, SemanticScalar)
    assert entry.value.text == "70"


def test_semantic_document_splits_consecutive_scalar_assignments_by_line() -> None:
    document = parse_semantic_document(
        "first_value = 1\n"
        "second_value = 2\n"
        "third_value = 3\n"
    )

    assert [entry.key for entry in document.entries] == [
        "first_value",
        "second_value",
        "third_value",
    ]
    values = [
        entry.value.text if isinstance(entry.value, SemanticScalar) else None
        for entry in document.entries
    ]

    assert values == [
        "1",
        "2",
        "3",
    ]


def test_semantic_document_splits_bom_prefixed_consecutive_scalar_assignments() -> None:
    document = parse_semantic_document(
        "\ufefffirst_value = 1\n"
        "second_value = 2\n"
        "third_value = 3\n"
    )

    assert [entry.key for entry in document.entries] == [
        "first_value",
        "second_value",
        "third_value",
    ]
