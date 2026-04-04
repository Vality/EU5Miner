"""Domain adapter for scripted trigger definitions."""

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
class ScriptedTriggerDefinition:
    """One scripted trigger definition."""

    name: str
    body: SemanticObject
    parameters: tuple[str, ...]
    entry: SemanticEntry


@dataclass(frozen=True)
class ScriptedTriggerDocument:
    """Parsed scripted trigger file."""

    definitions: tuple[ScriptedTriggerDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ScriptedTriggerDefinition | None:
        return get_by_name(self.definitions, name)


def parse_scripted_trigger_document(text: str) -> ScriptedTriggerDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ScriptedTriggerDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        parameters = tuple(sorted(collect_parameters_from_object(entry.value)))
        definitions.append(
            ScriptedTriggerDefinition(
                name=entry.key,
                body=entry.value,
                parameters=parameters,
                entry=entry,
            )
        )

    return ScriptedTriggerDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
