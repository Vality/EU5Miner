"""Domain adapter for building category definitions."""

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
class BuildingCategoryDefinition:
    """One building category definition."""

    name: str
    body: SemanticObject
    entry: SemanticEntry


@dataclass(frozen=True)
class BuildingCategoryDocument:
    """Parsed building category file."""

    definitions: tuple[BuildingCategoryDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> BuildingCategoryDefinition | None:
        return get_by_name(self.definitions, name)


def parse_building_category_document(text: str) -> BuildingCategoryDocument:
    semantic_document = parse_semantic_document(text)
    definitions = tuple(
        BuildingCategoryDefinition(name=entry.key, body=entry.value, entry=entry)
        for entry in semantic_document.entries
        if isinstance(entry.value, SemanticObject)
    )
    return BuildingCategoryDocument(
        definitions=definitions,
        semantic_document=semantic_document,
    )
