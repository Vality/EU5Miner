"""Domain adapter for religious figure definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ReligiousFigureDefinition:
    name: str
    body: SemanticObject
    enabled_for_religion: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ReligiousFigureDocument:
    definitions: tuple[ReligiousFigureDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> ReligiousFigureDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_religious_figure_document(text: str) -> ReligiousFigureDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ReligiousFigureDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            ReligiousFigureDefinition(
                name=entry.key,
                body=body,
                enabled_for_religion=body.get_object("enabled_for_religion"),
                entry=entry,
            )
        )

    return ReligiousFigureDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
