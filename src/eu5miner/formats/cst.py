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
class ScalarNode:
    """A scalar value represented by one or more non-trivia tokens."""

    tokens: tuple[Token, ...]

    @property
    def text(self) -> str:
        return " ".join(token.text for token in self.tokens)


@dataclass(frozen=True)
class StatementNode:
    """A top-level or nested statement in a Clausewitz-style document."""

    head_tokens: tuple[Token, ...]
    operator: Token | None
    value: ValueNode | None

    @property
    def head_text(self) -> str:
        return " ".join(token.text for token in self.head_tokens)


@dataclass(frozen=True)
class BlockNode:
    """A block value with optional prefix tokens such as `hsv360 { ... }`."""

    prefix_tokens: tuple[Token, ...]
    open_brace: Token
    entries: tuple[StatementNode, ...]
    close_brace: Token | None

    @property
    def prefix_text(self) -> str:
        return " ".join(token.text for token in self.prefix_tokens)


type ValueNode = ScalarNode | BlockNode


@dataclass(frozen=True)
class CstDocument:
    source_text: str
    tokens: tuple[Token, ...]
    entries: tuple[StatementNode, ...]

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
    if text.startswith("\ufeff"):
        text = text.removeprefix("\ufeff")

    tokens = tuple(tokenize_script_text(text))
    parser = _CstParser(text, tokens)
    entries = tuple(parser.parse_entries(stop_at_close_brace=False))
    return CstDocument(source_text=text, tokens=tokens, entries=entries)


def tokenize_script_text(text: str) -> list[Token]:
    if text.startswith("\ufeff"):
        text = text.removeprefix("\ufeff")

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
                tokens.append(Token(TokenKind.BRACKET_EXPRESSION, text[start:index], start, index))
            else:
                tokens.append(
                    Token(TokenKind.OPEN_BRACKET, text[start : start + 1], start, start + 1)
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


class _CstParser:
    def __init__(self, source_text: str, tokens: tuple[Token, ...]) -> None:
        self._source_text = source_text
        self._tokens = tokens
        self._index = 0

    def parse_entries(self, stop_at_close_brace: bool) -> list[StatementNode]:
        entries: list[StatementNode] = []

        while True:
            significant_index = self._next_significant_index(self._index)
            if significant_index is None:
                break

            next_token = self._tokens[significant_index]
            if stop_at_close_brace and next_token.kind == TokenKind.CLOSE_BRACE:
                break

            self._index = significant_index
            entries.append(self._parse_statement())

        return entries

    def _parse_statement(self) -> StatementNode:
        head_tokens = self._collect_same_line_tokens(
            stop_kinds={TokenKind.OPERATOR, TokenKind.OPEN_BRACE, TokenKind.CLOSE_BRACE}
        )

        operator_token = self._consume_if_kind(TokenKind.OPERATOR)
        if operator_token is not None:
            return StatementNode(
                head_tokens=tuple(head_tokens),
                operator=operator_token,
                value=self._parse_value(),
            )

        next_token = self._peek_significant_token()
        if next_token is not None and next_token.kind == TokenKind.OPEN_BRACE:
            return StatementNode(
                head_tokens=tuple(head_tokens),
                operator=None,
                value=self._parse_block(prefix_tokens=()),
            )

        return StatementNode(head_tokens=tuple(head_tokens), operator=None, value=None)

    def _parse_value(self) -> ValueNode:
        prefix_tokens = self._collect_same_line_tokens(
            stop_kinds={TokenKind.OPEN_BRACE, TokenKind.CLOSE_BRACE}
        )
        next_with_index = self._peek_significant()
        if next_with_index is not None:
            next_index, next_token = next_with_index
            if next_token.kind == TokenKind.OPEN_BRACE:
                if not prefix_tokens:
                    return self._parse_block(prefix_tokens=())

                last_prefix_index = self._find_last_consumed_index()
                if last_prefix_index is not None and not self._has_line_break_between(
                    last_prefix_index, next_index
                ):
                    return self._parse_block(prefix_tokens=tuple(prefix_tokens))

        if prefix_tokens:
            return ScalarNode(tokens=tuple(prefix_tokens))

        raise ValueError("Expected a value while parsing Clausewitz-style statement")

    def _parse_block(self, prefix_tokens: tuple[Token, ...]) -> BlockNode:
        open_brace = self._consume_expected(TokenKind.OPEN_BRACE)
        entries = tuple(self._parse_block_entries())
        close_brace = self._consume_if_kind(TokenKind.CLOSE_BRACE)
        return BlockNode(
            prefix_tokens=prefix_tokens,
            open_brace=open_brace,
            entries=entries,
            close_brace=close_brace,
        )

    def _parse_block_entries(self) -> list[StatementNode]:
        entries: list[StatementNode] = []

        while True:
            next_with_index = self._peek_significant()
            if next_with_index is None:
                break

            next_index, next_token = next_with_index
            if next_token.kind == TokenKind.CLOSE_BRACE:
                break

            line_indices = self._collect_same_line_significant_indices(next_index)

            if next_token.kind == TokenKind.OPEN_BRACE:
                self._index = next_index
                entries.append(
                    StatementNode(
                        head_tokens=(),
                        operator=None,
                        value=self._parse_block(prefix_tokens=()),
                    )
                )
                continue

            if any(self._tokens[index].kind == TokenKind.OPERATOR for index in line_indices):
                self._index = next_index
                entries.append(self._parse_statement())
                continue

            self._index = next_index + 1
            entries.append(
                StatementNode(
                    head_tokens=(next_token,),
                    operator=None,
                    value=None,
                )
            )

        return entries

    def _collect_same_line_tokens(self, stop_kinds: set[TokenKind]) -> list[Token]:
        collected: list[Token] = []

        while True:
            next_with_index = self._peek_significant()
            if next_with_index is None:
                break

            next_index, next_token = next_with_index
            if next_token.kind in stop_kinds:
                break

            self._index = next_index + 1
            collected.append(next_token)

            following = self._peek_significant()
            if following is None:
                break

            following_index, following_token = following
            if following_token.kind in stop_kinds:
                continue

            if self._has_line_break_between(next_index, following_index):
                break

        return collected

    def _peek_significant(self) -> tuple[int, Token] | None:
        next_index = self._next_significant_index(self._index)
        if next_index is None:
            return None
        return next_index, self._tokens[next_index]

    def _peek_significant_token(self) -> Token | None:
        next_with_index = self._peek_significant()
        if next_with_index is None:
            return None
        return next_with_index[1]

    def _peek_significant_from(self, start: int) -> tuple[int, Token] | None:
        next_index = self._next_significant_index(start)
        if next_index is None:
            return None
        return next_index, self._tokens[next_index]

    def _collect_same_line_significant_indices(self, start_index: int) -> list[int]:
        indices = [start_index]
        current_index = start_index

        while True:
            following = self._peek_significant_from(current_index + 1)
            if following is None:
                break

            following_index, following_token = following
            if following_token.kind == TokenKind.CLOSE_BRACE:
                break
            if self._has_line_break_between(current_index, following_index):
                break

            indices.append(following_index)
            current_index = following_index

        return indices

    def _next_significant_index(self, start: int) -> int | None:
        for index in range(start, len(self._tokens)):
            if self._tokens[index].kind not in {TokenKind.WHITESPACE, TokenKind.COMMENT}:
                return index
        return None

    def _consume_if_kind(self, kind: TokenKind) -> Token | None:
        next_with_index = self._peek_significant()
        if next_with_index is None:
            return None

        next_index, token = next_with_index
        if token.kind != kind:
            return None

        self._index = next_index + 1
        return token

    def _consume_expected(self, kind: TokenKind) -> Token:
        token = self._consume_if_kind(kind)
        if token is None:
            raise ValueError(f"Expected token kind {kind.value}")
        return token

    def _find_last_consumed_index(self) -> int | None:
        last_index = self._index - 1
        if last_index < 0:
            return None
        return last_index

    def _has_line_break_between(self, left_index: int, right_index: int) -> bool:
        left_token = self._tokens[left_index]
        right_token = self._tokens[right_index]
        return "\n" in self._source_text[left_token.end : right_token.start]
