"""Domain adapter for scripted list definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._macros import collect_parameters_from_object
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ScriptedListDefinition:
    """One scripted list definition."""

    name: str
    body: SemanticObject
    base: str | None
    conditions: SemanticObject | None
    parameters: tuple[str, ...]
    entry: SemanticEntry


@dataclass(frozen=True)
class ScriptedListDocument:
    """Parsed scripted list file."""

    definitions: tuple[ScriptedListDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ScriptedListDefinition | None:
        return get_by_name(self.definitions, name)


def parse_scripted_list_document(text: str) -> ScriptedListDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ScriptedListDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        definitions.append(
            ScriptedListDefinition(
                name=entry.key,
                body=entry.value,
                base=entry.value.get_scalar("base"),
                conditions=entry.value.get_object("conditions"),
                parameters=tuple(sorted(collect_parameters_from_object(entry.value))),
                entry=entry,
            )
        )

    return ScriptedListDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
