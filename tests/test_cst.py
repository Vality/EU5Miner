from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.formats.cst import (
    BlockNode,
    CstDocument,
    ScalarNode,
    TokenKind,
    parse_cst_document,
    tokenize_script_text,
)
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_tokenizer_detects_macros_comments_and_operators() -> None:
    tokens = tokenize_script_text(
        '# comment\ncountry_rank_is_what = { value ?= $target_rank$ }\n'
    )
    kinds = [token.kind for token in tokens]

    assert TokenKind.COMMENT in kinds
    assert TokenKind.OPERATOR in kinds
    assert TokenKind.MACRO in kinds
    assert TokenKind.OPEN_BRACE in kinds
    assert TokenKind.CLOSE_BRACE in kinds


@pytest.mark.timeout(5)
def test_parse_real_script_file_to_balanced_document(game_install: GameInstall) -> None:
    document = parse_cst_document(
        _read_text(game_install.representative_files()["scripted_trigger"])
    )

    assert isinstance(document, CstDocument)
    assert document.is_brace_balanced
    assert len(document.non_trivia_tokens()) > 10
    assert len(document.entries) > 5
    assert document.entries[0].head_text == "country_can_ennoble_trigger"
    assert document.entries[0].operator is not None
    assert isinstance(document.entries[0].value, BlockNode)


@pytest.mark.timeout(5)
def test_parse_real_gui_file_detects_bracket_expressions(game_install: GameInstall) -> None:
    document = parse_cst_document(_read_text(game_install.representative_files()["gui_sample"]))

    assert document.is_brace_balanced
    assert any(token.kind == TokenKind.BRACKET_EXPRESSION for token in document.tokens)
    assert document.entries[0].head_text == "template agenda_scrollarea_setup"
    assert isinstance(document.entries[0].value, BlockNode)


def test_grouping_supports_typed_block_values() -> None:
    document = parse_cst_document("color = hsv360 { 360 100 100 }\n")

    assert len(document.entries) == 1
    entry = document.entries[0]
    assert entry.head_text == "color"
    assert entry.operator is not None
    assert isinstance(entry.value, BlockNode)
    assert entry.value.prefix_text == "hsv360"
    assert [nested.head_text for nested in entry.value.entries] == ["360", "100", "100"]


def test_grouping_supports_scalar_assignments() -> None:
    document = parse_cst_document("prestige > 70\n")

    assert len(document.entries) == 1
    entry = document.entries[0]
    assert entry.head_text == "prestige"
    assert entry.operator is not None
    assert isinstance(entry.value, ScalarNode)
    assert entry.value.text == "70"


def test_grouping_splits_consecutive_scalar_assignments_by_line() -> None:
    document = parse_cst_document(
        "first_value = 1\n"
        "second_value = 2\n"
        "third_value = 3\n"
    )

    assert [entry.head_text for entry in document.entries] == [
        "first_value",
        "second_value",
        "third_value",
    ]
    values = [
        entry.value.text if isinstance(entry.value, ScalarNode) else None
        for entry in document.entries
    ]

    assert values == [
        "1",
        "2",
        "3",
    ]


def test_grouping_splits_bom_prefixed_consecutive_scalar_assignments() -> None:
    document = parse_cst_document(
        "\ufefffirst_value = 1\n"
        "second_value = 2\n"
        "third_value = 3\n"
    )

    assert [entry.head_text for entry in document.entries] == [
        "first_value",
        "second_value",
        "third_value",
    ]
