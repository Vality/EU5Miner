"""Domain adapter for government type definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import parse_bool_or_none, parse_int_or_none
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class GovernmentTypeDefinition:
    name: str
    body: SemanticObject
    use_regnal_number: bool | None
    generate_consorts: bool | None
    heir_selections: tuple[str, ...]
    map_color: str | None
    government_power: str | None
    revolutionary_country_antagonism: int | None
    default_character_estate: str | None
    modifier: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class GovernmentTypeDocument:
    definitions: tuple[GovernmentTypeDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> GovernmentTypeDefinition | None:
        return get_by_name(self.definitions, name)


def parse_government_type_document(text: str) -> GovernmentTypeDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[GovernmentTypeDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            GovernmentTypeDefinition(
                name=entry.key,
                body=body,
                use_regnal_number=parse_bool_or_none(body.get_scalar("use_regnal_number")),
                generate_consorts=parse_bool_or_none(body.get_scalar("generate_consorts")),
                heir_selections=tuple(
                    child.value.text
                    for child in body.find_entries("heir_selection")
                    if child.value is not None and hasattr(child.value, "text")
                ),
                map_color=body.get_scalar("map_color"),
                government_power=body.get_scalar("government_power"),
                revolutionary_country_antagonism=parse_int_or_none(
                    body.get_scalar("revolutionary_country_antagonism")
                ),
                default_character_estate=body.get_scalar("default_character_estate"),
                modifier=body.get_object("modifier"),
                entry=entry,
            )
        )

    return GovernmentTypeDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
