"""Domain adapter for setup country definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class SetupCountryDefinition:
    """One setup-country definition keyed by country tag."""

    tag: str
    body: SemanticObject
    color: str | None
    color2: str | None
    culture_definition: str | None
    religion_definition: str | None
    description_category: str | None
    difficulty: int | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class SetupCountryDocument:
    """Parsed setup-country file."""

    definitions: tuple[SetupCountryDefinition, ...]
    semantic_document: SemanticDocument

    def tags(self) -> tuple[str, ...]:
        return tuple(definition.tag for definition in self.definitions)

    def get_definition(self, tag: str) -> SetupCountryDefinition | None:
        for definition in self.definitions:
            if definition.tag == tag:
                return definition
        return None


def parse_setup_country_document(text: str) -> SetupCountryDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[SetupCountryDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        difficulty_text = entry.value.get_scalar("difficulty")
        definitions.append(
            SetupCountryDefinition(
                tag=entry.key,
                body=entry.value,
                color=_get_value_text(entry.value, "color"),
                color2=_get_value_text(entry.value, "color2"),
                culture_definition=entry.value.get_scalar("culture_definition"),
                religion_definition=entry.value.get_scalar("religion_definition"),
                description_category=entry.value.get_scalar("description_category"),
                difficulty=_parse_int_or_none(difficulty_text),
                entry=entry,
            )
        )

    return SetupCountryDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_int_or_none(value: str | None) -> int | None:
    if value is None:
        return None
    return int(value)


def _get_value_text(body: SemanticObject, key: str) -> str | None:
    entry = body.first_entry(key)
    if entry is None or entry.value is None:
        return None
    if hasattr(entry.value, "text"):
        return entry.value.text
    if isinstance(entry.value, SemanticObject):
        return entry.value.prefix or None
    return None
