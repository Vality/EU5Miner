"""Domain adapter for holy site type definitions."""

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
class HolySiteTypeDefinition:
    name: str
    body: SemanticObject
    country_modifier: SemanticObject | None
    location_modifier: SemanticObject | None
    religion_modifier: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class HolySiteTypeDocument:
    definitions: tuple[HolySiteTypeDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> HolySiteTypeDefinition | None:
        return get_by_name(self.definitions, name)


def parse_holy_site_type_document(text: str) -> HolySiteTypeDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[HolySiteTypeDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            HolySiteTypeDefinition(
                name=entry.key,
                body=body,
                country_modifier=body.get_object("country_modifier"),
                location_modifier=body.get_object("location_modifier"),
                religion_modifier=body.get_object("religion_modifier"),
                entry=entry,
            )
        )

    return HolySiteTypeDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
