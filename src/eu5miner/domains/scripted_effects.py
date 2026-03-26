"""Domain adapter for scripted effect definitions."""

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
class ScriptedEffectDefinition:
    """One scripted effect definition."""

    name: str
    body: SemanticObject
    parameters: tuple[str, ...]
    entry: SemanticEntry


@dataclass(frozen=True)
class ScriptedEffectDocument:
    """Parsed scripted effect file."""

    definitions: tuple[ScriptedEffectDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ScriptedEffectDefinition | None:
        return get_by_name(self.definitions, name)


def parse_scripted_effect_document(text: str) -> ScriptedEffectDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ScriptedEffectDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        definitions.append(
            ScriptedEffectDefinition(
                name=entry.key,
                body=entry.value,
                parameters=tuple(sorted(collect_parameters_from_object(entry.value))),
                entry=entry,
            )
        )

    return ScriptedEffectDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
