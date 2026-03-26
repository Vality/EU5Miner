"""Domain adapter for parliament type definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ParliamentTypeDefinition:
    name: str
    body: SemanticObject
    parliament_type: str | None
    potential: SemanticObject | None
    allow: SemanticObject | None
    locked: SemanticObject | None
    modifier: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ParliamentTypeDocument:
    definitions: tuple[ParliamentTypeDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ParliamentTypeDefinition | None:
        return get_by_name(self.definitions, name)


def parse_parliament_type_document(text: str) -> ParliamentTypeDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ParliamentTypeDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            ParliamentTypeDefinition(
                name=entry.key,
                body=body,
                parliament_type=body.get_scalar("type"),
                potential=body.get_object("potential"),
                allow=body.get_object("allow"),
                locked=body.get_object("locked"),
                modifier=body.get_object("modifier"),
                entry=entry,
            )
        )

    return ParliamentTypeDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
