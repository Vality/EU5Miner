"""Domain adapter for religious faction definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._parse_helpers import collect_scalar_like_values
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ReligiousFactionDefinition:
    name: str
    body: SemanticObject
    visible: SemanticObject | None
    enabled: SemanticObject | None
    actions: tuple[str, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ReligiousFactionDocument:
    definitions: tuple[ReligiousFactionDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ReligiousFactionDefinition | None:
        return get_by_name(self.definitions, name)


def parse_religious_faction_document(text: str) -> ReligiousFactionDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ReligiousFactionDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            ReligiousFactionDefinition(
                name=entry.key,
                body=body,
                visible=body.get_object("visible"),
                enabled=body.get_object("enabled"),
                actions=collect_scalar_like_values(body.first_entry("actions")),
                entry=entry,
            )
        )

    return ReligiousFactionDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
