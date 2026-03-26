"""Domain adapter for goods demand category definitions."""

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
class GoodsDemandCategoryDefinition:
    """One goods demand category definition."""

    name: str
    body: SemanticObject
    display: str | None
    entry: SemanticEntry


@dataclass(frozen=True)
class GoodsDemandCategoryDocument:
    """Parsed goods demand category file."""

    definitions: tuple[GoodsDemandCategoryDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> GoodsDemandCategoryDefinition | None:
        return get_by_name(self.definitions, name)


def parse_goods_demand_category_document(text: str) -> GoodsDemandCategoryDocument:
    semantic_document = parse_semantic_document(text)
    definitions = tuple(
        GoodsDemandCategoryDefinition(
            name=entry.key,
            body=entry.value,
            display=entry.value.get_scalar("display"),
            entry=entry,
        )
        for entry in semantic_document.entries
        if isinstance(entry.value, SemanticObject)
    )
    return GoodsDemandCategoryDocument(
        definitions=definitions,
        semantic_document=semantic_document,
    )
