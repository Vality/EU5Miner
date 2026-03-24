"""Semantic helpers built on top of the first-pass CST model."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats import cst

type SemanticValue = SemanticScalar | SemanticObject


@dataclass(frozen=True)
class SemanticScalar:
    """Semantic scalar value extracted from CST scalar tokens."""

    text: str
    node: cst.ScalarNode


@dataclass(frozen=True)
class SemanticEntry:
    """Key/operator/value semantic entry backed by a CST statement."""

    key: str
    operator: str | None
    value: SemanticValue | None
    node: cst.StatementNode

    @property
    def is_object_like(self) -> bool:
        return isinstance(self.value, SemanticObject)


@dataclass(frozen=True)
class SemanticObject:
    """Object-like block value with helper accessors for child entries."""

    entries: tuple[SemanticEntry, ...]
    node: cst.BlockNode

    @property
    def prefix(self) -> str:
        return self.node.prefix_text

    def find_entries(self, key: str) -> tuple[SemanticEntry, ...]:
        return tuple(entry for entry in self.entries if entry.key == key)

    def first_entry(self, key: str) -> SemanticEntry | None:
        matches = self.find_entries(key)
        if not matches:
            return None
        return matches[0]

    def get_scalar(self, key: str) -> str | None:
        entry = self.first_entry(key)
        if entry is None or not isinstance(entry.value, SemanticScalar):
            return None
        return entry.value.text

    def get_object(self, key: str) -> SemanticObject | None:
        entry = self.first_entry(key)
        if entry is None or not isinstance(entry.value, SemanticObject):
            return None
        return entry.value


@dataclass(frozen=True)
class SemanticDocument:
    """Semantic view of a parsed Clausewitz-style document."""

    entries: tuple[SemanticEntry, ...]
    cst_document: cst.CstDocument

    def find_entries(self, key: str) -> tuple[SemanticEntry, ...]:
        return tuple(entry for entry in self.entries if entry.key == key)

    def first_entry(self, key: str) -> SemanticEntry | None:
        matches = self.find_entries(key)
        if not matches:
            return None
        return matches[0]


def parse_semantic_document(text: str) -> SemanticDocument:
    cst_document = cst.parse_cst_document(text)
    entries = tuple(_semantic_entry_from_statement(entry) for entry in cst_document.entries)
    return SemanticDocument(entries=entries, cst_document=cst_document)


def _semantic_entry_from_statement(statement: cst.StatementNode) -> SemanticEntry:
    return SemanticEntry(
        key=statement.head_text,
        operator=statement.operator.text if statement.operator is not None else None,
        value=_semantic_value_from_cst(statement.value),
        node=statement,
    )


def _semantic_value_from_cst(value: object | None) -> SemanticValue | None:
    if value is None:
        return None
    if isinstance(value, cst.ScalarNode):
        return SemanticScalar(text=value.text, node=value)
    if isinstance(value, cst.BlockNode):
        return SemanticObject(
            entries=tuple(_semantic_entry_from_statement(entry) for entry in value.entries),
            node=value,
        )
    raise TypeError(f"Unsupported CST value type: {type(value)!r}")
