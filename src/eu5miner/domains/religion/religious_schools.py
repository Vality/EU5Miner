"""Domain adapter for religious school definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import body_value_text
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ReligiousSchoolDefinition:
    name: str
    body: SemanticObject
    color: str | None
    enabled_for_country: SemanticObject | None
    enabled_for_character: SemanticObject | None
    modifier: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ReligiousSchoolDocument:
    definitions: tuple[ReligiousSchoolDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ReligiousSchoolDefinition | None:
        return get_by_name(self.definitions, name)


def parse_religious_school_document(text: str) -> ReligiousSchoolDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ReligiousSchoolDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            ReligiousSchoolDefinition(
                name=entry.key,
                body=body,
                color=body_value_text(body, "color"),
                enabled_for_country=body.get_object("enabled_for_country"),
                enabled_for_character=body.get_object("enabled_for_character"),
                modifier=body.get_object("modifier"),
                entry=entry,
            )
        )

    return ReligiousSchoolDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
