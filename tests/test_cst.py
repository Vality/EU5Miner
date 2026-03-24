from __future__ import annotations

from pathlib import Path

from eu5miner.formats.cst import CstDocument, TokenKind, parse_cst_document, tokenize_script_text
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


def test_parse_real_script_file_to_balanced_document(game_install: GameInstall) -> None:
    document = parse_cst_document(
        _read_text(game_install.representative_files()["scripted_trigger"])
    )

    assert isinstance(document, CstDocument)
    assert document.is_brace_balanced
    assert len(document.non_trivia_tokens()) > 10


def test_parse_real_gui_file_detects_bracket_expressions(game_install: GameInstall) -> None:
    document = parse_cst_document(_read_text(game_install.representative_files()["gui_sample"]))

    assert document.is_brace_balanced
    assert any(token.kind == TokenKind.BRACKET_EXPRESSION for token in document.tokens)
