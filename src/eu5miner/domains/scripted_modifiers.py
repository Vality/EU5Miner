"""Domain adapter for scripted modifier definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._macros import collect_parameters_from_object
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ScriptedModifierDefinition:
    """One scripted modifier definition."""

    name: str
    body: SemanticObject
    modifier: SemanticObject | None
    opinion_modifier: SemanticObject | None
    compare_modifier: SemanticObject | None
    parameters: tuple[str, ...]
    entry: SemanticEntry


@dataclass(frozen=True)
class ScriptedModifierDocument:
    """Parsed scripted modifier file."""

    definitions: tuple[ScriptedModifierDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ScriptedModifierDefinition | None:
        return get_by_name(self.definitions, name)


def parse_scripted_modifier_document(text: str) -> ScriptedModifierDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ScriptedModifierDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        definitions.append(
            ScriptedModifierDefinition(
                name=entry.key,
                body=entry.value,
                modifier=entry.value.get_object("modifier"),
                opinion_modifier=entry.value.get_object("opinion_modifier"),
                compare_modifier=entry.value.get_object("compare_modifier"),
                parameters=tuple(sorted(collect_parameters_from_object(entry.value))),
                entry=entry,
            )
        )

    return ScriptedModifierDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
