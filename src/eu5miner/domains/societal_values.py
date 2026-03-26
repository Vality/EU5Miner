"""Domain adapter for societal value axis definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import parse_float_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class SocietalValueDefinition:
    name: str
    body: SemanticObject
    left_modifier: SemanticObject | None
    right_modifier: SemanticObject | None
    opinion_importance_multiplier: float | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class SocietalValueDocument:
    definitions: tuple[SocietalValueDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> SocietalValueDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_societal_value_document(text: str) -> SocietalValueDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[SocietalValueDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            SocietalValueDefinition(
                name=entry.key,
                body=body,
                left_modifier=body.get_object("left_modifier"),
                right_modifier=body.get_object("right_modifier"),
                opinion_importance_multiplier=parse_float_or_none(
                    body.get_scalar("opinion_importance_multiplier")
                ),
                entry=entry,
            )
        )

    return SocietalValueDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )