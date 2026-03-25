"""Domain adapter for scripted value definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._macros import collect_parameters_from_object
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ScriptValueDefinition:
    """One scripted value definition."""

    name: str
    value: SemanticScalar | SemanticObject
    parameters: tuple[str, ...]
    entry: SemanticEntry

    @property
    def is_scalar(self) -> bool:
        return isinstance(self.value, SemanticScalar)

    @property
    def is_formula(self) -> bool:
        return isinstance(self.value, SemanticObject)

    @property
    def scalar_text(self) -> str | None:
        if not isinstance(self.value, SemanticScalar):
            return None
        return self.value.text

    @property
    def formula(self) -> SemanticObject | None:
        if not isinstance(self.value, SemanticObject):
            return None
        return self.value


@dataclass(frozen=True)
class ScriptValueDocument:
    """Parsed scripted value file."""

    definitions: tuple[ScriptValueDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> ScriptValueDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_script_value_document(text: str) -> ScriptValueDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ScriptValueDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticScalar | SemanticObject):
            continue

        definitions.append(
            ScriptValueDefinition(
                name=entry.key,
                value=entry.value,
                parameters=_collect_parameters(entry.value),
                entry=entry,
            )
        )

    return ScriptValueDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _collect_parameters(value: SemanticScalar | SemanticObject) -> tuple[str, ...]:
    if isinstance(value, SemanticScalar):
        return ()
    return tuple(sorted(collect_parameters_from_object(value)))
