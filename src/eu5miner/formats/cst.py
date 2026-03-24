"""Minimal CST tokenizer and document model for Clausewitz-style text."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TokenKind(StrEnum):
    """Token kinds preserved by the initial CST layer."""

    WHITESPACE = "whitespace"
    COMMENT = "comment"
    OPEN_BRACE = "open_brace"
    CLOSE_BRACE = "close_brace"
    OPEN_BRACKET = "open_bracket"
    CLOSE_BRACKET = "close_bracket"
    OPERATOR = "operator"
    STRING = "string"
    MACRO = "macro"
    BRACKET_EXPRESSION = "bracket_expression"
    ATOM = "atom"


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class CstDocument:
    source_text: str
    tokens: tuple[Token, ...]

    @property
    def is_brace_balanced(self) -> bool:
        depth = 0
        for token in self.tokens:
            if token.kind == TokenKind.OPEN_BRACE:
                depth += 1
            elif token.kind == TokenKind.CLOSE_BRACE:
                depth -= 1
                if depth < 0:
                    return False
        return depth == 0

    def non_trivia_tokens(self) -> tuple[Token, ...]:
        return tuple(
            token
            for token in self.tokens
            if token.kind not in {TokenKind.WHITESPACE, TokenKind.COMMENT}
        )


def parse_cst_document(text: str) -> CstDocument:
    return CstDocument(source_text=text, tokens=tuple(tokenize_script_text(text)))


def tokenize_script_text(text: str) -> list[Token]:
    tokens: list[Token] = []
    index = 0
    length = len(text)

    while index < length:
        char = text[index]

        if char.isspace():
            start = index
            while index < length and text[index].isspace():
                index += 1
            tokens.append(Token(TokenKind.WHITESPACE, text[start:index], start, index))
            continue

        if char == "#":
            start = index
            while index < length and text[index] != "\n":
                index += 1
            tokens.append(Token(TokenKind.COMMENT, text[start:index], start, index))
            continue

        if char == '"':
            start = index
            index += 1
            escaped = False
            while index < length:
                current = text[index]
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == '"':
                    index += 1
                    break
                index += 1
            token_text = text[start:index]
            token_kind = _classify_string_token(token_text)
            tokens.append(Token(token_kind, token_text, start, index))
            continue

        if char == "$":
            start = index
            index += 1
            while index < length and text[index] != "$":
                index += 1
            if index < length:
                index += 1
            tokens.append(Token(TokenKind.MACRO, text[start:index], start, index))
            continue

        if char == "[":
            start = index
            index += 1
            while index < length and text[index] != "]":
                if text[index] == '"':
                    string_start = index
                    index += 1
                    escaped = False
                    while index < length:
                        current = text[index]
                        if escaped:
                            escaped = False
                        elif current == "\\":
                            escaped = True
                        elif current == '"':
                            index += 1
                            break
                        index += 1
                    if index == string_start + 1:
                        break
                    continue
                index += 1
            if index < length and text[index] == "]":
                index += 1
                tokens.append(
                    Token(TokenKind.BRACKET_EXPRESSION, text[start:index], start, index)
                )
            else:
                tokens.append(
                    Token(TokenKind.OPEN_BRACKET, text[start:start + 1], start, start + 1)
                )
            continue

        if char == "{":
            tokens.append(Token(TokenKind.OPEN_BRACE, char, index, index + 1))
            index += 1
            continue

        if char == "}":
            tokens.append(Token(TokenKind.CLOSE_BRACE, char, index, index + 1))
            index += 1
            continue

        if char == "]":
            tokens.append(Token(TokenKind.CLOSE_BRACKET, char, index, index + 1))
            index += 1
            continue

        operator_match = _match_operator(text, index)
        if operator_match is not None:
            operator_text = operator_match
            end = index + len(operator_text)
            tokens.append(Token(TokenKind.OPERATOR, operator_text, index, end))
            index = end
            continue

        start = index
        while index < length and not _is_token_boundary(text[index]):
            index += 1
        tokens.append(Token(TokenKind.ATOM, text[start:index], start, index))

    return tokens


def _match_operator(text: str, index: int) -> str | None:
    for operator in ("<=", ">=", "!=", "?=", "=", "<", ">"):
        if text.startswith(operator, index):
            return operator
    return None


def _is_token_boundary(char: str) -> bool:
    return char.isspace() or char in '#"${}[]=<>'


def _classify_string_token(token_text: str) -> TokenKind:
    if len(token_text) >= 4 and token_text[0] == '"' and token_text[-1] == '"':
        inner_text = token_text[1:-1]
        if inner_text.startswith("[") and inner_text.endswith("]"):
            return TokenKind.BRACKET_EXPRESSION
    return TokenKind.STRING
