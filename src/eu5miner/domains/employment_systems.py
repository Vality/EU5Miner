"""Domain adapter for employment system definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class EmploymentSystemDefinition:
    """One employment system definition."""

    name: str
    body: SemanticObject
    country_modifier: SemanticObject | None
    priority: SemanticObject | None
    ai_will_do: SemanticObject | None
    entry: SemanticEntry


@dataclass(frozen=True)
class EmploymentSystemDocument:
    """Parsed employment system file."""

    definitions: tuple[EmploymentSystemDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> EmploymentSystemDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_employment_system_document(text: str) -> EmploymentSystemDocument:
    semantic_document = parse_semantic_document(text)
    definitions = tuple(
        EmploymentSystemDefinition(
            name=entry.key,
            body=entry.value,
            country_modifier=entry.value.get_object("country_modifier"),
            priority=entry.value.get_object("priority"),
            ai_will_do=entry.value.get_object("ai_will_do"),
            entry=entry,
        )
        for entry in semantic_document.entries
        if isinstance(entry.value, SemanticObject)
    )
    return EmploymentSystemDocument(
        definitions=definitions,
        semantic_document=semantic_document,
    )
