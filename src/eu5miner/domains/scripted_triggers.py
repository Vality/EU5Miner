"""Domain adapter for scripted trigger definitions."""

from __future__ import annotations

import re
from dataclasses import dataclass

from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)

MACRO_NAME_RE = re.compile(r"\$([A-Za-z0-9_]+)\$")


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
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> ScriptedTriggerDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_scripted_trigger_document(text: str) -> ScriptedTriggerDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ScriptedTriggerDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        parameters = tuple(sorted(_collect_parameters_from_object(entry.value)))
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


def _collect_parameters_from_object(value: SemanticObject) -> set[str]:
    parameters: set[str] = set()

    if value.prefix:
        parameters.update(MACRO_NAME_RE.findall(value.prefix))

    for entry in value.entries:
        parameters.update(MACRO_NAME_RE.findall(entry.key))
        if entry.operator is not None:
            parameters.update(MACRO_NAME_RE.findall(entry.operator))

        child_value = entry.value
        if child_value is None:
            continue
        if hasattr(child_value, "text"):
            parameters.update(MACRO_NAME_RE.findall(child_value.text))
        if isinstance(child_value, SemanticObject):
            parameters.update(_collect_parameters_from_object(child_value))

    return parameters
