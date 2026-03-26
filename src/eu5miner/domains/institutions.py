"""Domain adapter for institution definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)


@dataclass(frozen=True)
class InstitutionDefinition:
    name: str
    body: SemanticObject
    age: str | None
    location: str | None
    can_spawn: SemanticObject | None
    promote_chance: str | SemanticObject | None
    spread_from_friendly_coast_border_location: str | SemanticObject | None
    spread_from_any_coast_border_location: str | SemanticObject | None
    spread_from_any_import: str | SemanticObject | None
    spread_from_any_export: str | SemanticObject | None
    spread_from_was_possible_spawn: str | SemanticObject | None
    spread_scale_on_control_if_owner_embraced: str | SemanticObject | None
    spread_embraced_to_capital: str | SemanticObject | None
    spread_to_market_member: str | SemanticObject | None
    spread: str | SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class InstitutionDocument:
    definitions: tuple[InstitutionDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> InstitutionDefinition | None:
        return get_by_name(self.definitions, name)


def parse_institution_document(text: str) -> InstitutionDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[InstitutionDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            InstitutionDefinition(
                name=entry.key,
                body=body,
                age=body.get_scalar("age"),
                location=body.get_scalar("location"),
                can_spawn=body.get_object("can_spawn"),
                promote_chance=_parse_scalar_or_object(body.first_entry("promote_chance")),
                spread_from_friendly_coast_border_location=_parse_scalar_or_object(
                    body.first_entry("spread_from_friendly_coast_border_location")
                ),
                spread_from_any_coast_border_location=_parse_scalar_or_object(
                    body.first_entry("spread_from_any_coast_border_location")
                ),
                spread_from_any_import=_parse_scalar_or_object(
                    body.first_entry("spread_from_any_import")
                ),
                spread_from_any_export=_parse_scalar_or_object(
                    body.first_entry("spread_from_any_export")
                ),
                spread_from_was_possible_spawn=_parse_scalar_or_object(
                    body.first_entry("spread_from_was_possible_spawn")
                ),
                spread_scale_on_control_if_owner_embraced=_parse_scalar_or_object(
                    body.first_entry("spread_scale_on_control_if_owner_embraced")
                ),
                spread_embraced_to_capital=_parse_scalar_or_object(
                    body.first_entry("spread_embraced_to_capital")
                ),
                spread_to_market_member=_parse_scalar_or_object(
                    body.first_entry("spread_to_market_member")
                ),
                spread=_parse_scalar_or_object(body.first_entry("spread")),
                entry=entry,
            )
        )

    return InstitutionDocument(definitions=tuple(definitions), semantic_document=semantic_document)


def _parse_scalar_or_object(entry: SemanticEntry | None) -> str | SemanticObject | None:
    if entry is None:
        return None
    if isinstance(entry.value, SemanticScalar):
        return entry.value.text
    if isinstance(entry.value, SemanticObject):
        return entry.value
    return None
