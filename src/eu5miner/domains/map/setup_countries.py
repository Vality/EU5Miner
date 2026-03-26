"""Domain adapter for setup country definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_tag, tags_from_tagged
from eu5miner.domains._parse_helpers import body_value_text, parse_int_or_none
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
        return tags_from_tagged(self.definitions)

    def get_definition(self, tag: str) -> SetupCountryDefinition | None:
        return get_by_tag(self.definitions, tag)


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
                color=body_value_text(entry.value, "color"),
                color2=body_value_text(entry.value, "color2"),
                culture_definition=entry.value.get_scalar("culture_definition"),
                religion_definition=entry.value.get_scalar("religion_definition"),
                description_category=entry.value.get_scalar("description_category"),
                difficulty=parse_int_or_none(difficulty_text),
                entry=entry,
            )
        )

    return SetupCountryDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
