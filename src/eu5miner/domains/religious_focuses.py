"""Domain adapter for religious focus definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ReligiousFocusDefinition:
    name: str
    body: SemanticObject
    potential: SemanticObject | None
    allow: SemanticObject | None
    monthly_progress: SemanticObject | None
    modifier_while_progressing: SemanticObject | None
    modifier_on_completion: SemanticObject | None
    effect_on_completion: SemanticObject | None
    ai_will_do: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ReligiousFocusDocument:
    definitions: tuple[ReligiousFocusDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> ReligiousFocusDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_religious_focus_document(text: str) -> ReligiousFocusDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ReligiousFocusDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            ReligiousFocusDefinition(
                name=entry.key,
                body=body,
                potential=body.get_object("potential"),
                allow=body.get_object("allow"),
                monthly_progress=body.get_object("monthly_progress"),
                modifier_while_progressing=body.get_object("modifier_while_progressing"),
                modifier_on_completion=body.get_object("modifier_on_completion"),
                effect_on_completion=body.get_object("effect_on_completion"),
                ai_will_do=body.get_object("ai_will_do"),
                entry=entry,
            )
        )

    return ReligiousFocusDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )