"""Domain adapter for production method definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._parse_helpers import parse_bool_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ProductionMethodInput:
    """One scalar goods input entry inside a production method."""

    goods: str
    amount: str
    entry: SemanticEntry


@dataclass(frozen=True)
class ProductionMethodDefinition:
    """One production method definition."""

    name: str
    body: SemanticObject
    category: str | None
    produced: str | None
    output: str | None
    no_upkeep: bool | None
    potential: SemanticObject | None
    allow: SemanticObject | None
    inputs: tuple[ProductionMethodInput, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ProductionMethodDocument:
    """Parsed production method file."""

    definitions: tuple[ProductionMethodDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ProductionMethodDefinition | None:
        return get_by_name(self.definitions, name)


def parse_production_method_document(text: str) -> ProductionMethodDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ProductionMethodDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        inputs: list[ProductionMethodInput] = []
        for child in body.entries:
            if child.key in {"category", "produced", "output", "potential", "no_upkeep", "allow"}:
                continue
            if isinstance(child.value, SemanticScalar):
                inputs.append(
                    ProductionMethodInput(
                        goods=child.key,
                        amount=child.value.text,
                        entry=child,
                    )
                )

        definitions.append(
            ProductionMethodDefinition(
                name=entry.key,
                body=body,
                category=body.get_scalar("category"),
                produced=body.get_scalar("produced"),
                output=body.get_scalar("output"),
                no_upkeep=parse_bool_or_none(body.get_scalar("no_upkeep")),
                potential=body.get_object("potential"),
                allow=body.get_object("allow"),
                inputs=tuple(inputs),
                entry=entry,
            )
        )

    return ProductionMethodDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
