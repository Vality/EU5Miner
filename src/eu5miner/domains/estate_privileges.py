"""Domain adapter for estate privilege definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._parse_helpers import parse_int_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class EstatePrivilegeDefinition:
    name: str
    body: SemanticObject
    estate: str | None
    potential: SemanticObject | None
    allow: SemanticObject | None
    can_revoke: SemanticObject | None
    on_activate: SemanticObject | None
    on_fully_activated: SemanticObject | None
    on_deactivate: SemanticObject | None
    country_modifiers: tuple[SemanticObject, ...]
    province_modifiers: tuple[SemanticObject, ...]
    location_modifiers: tuple[SemanticObject, ...]
    years: int | None
    months: int | None
    weeks: int | None
    days: int | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class EstatePrivilegeDocument:
    definitions: tuple[EstatePrivilegeDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> EstatePrivilegeDefinition | None:
        return get_by_name(self.definitions, name)


def parse_estate_privilege_document(text: str) -> EstatePrivilegeDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[EstatePrivilegeDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            EstatePrivilegeDefinition(
                name=entry.key,
                body=body,
                estate=body.get_scalar("estate"),
                potential=body.get_object("potential"),
                allow=body.get_object("allow"),
                can_revoke=body.get_object("can_revoke"),
                on_activate=body.get_object("on_activate"),
                on_fully_activated=body.get_object("on_fully_activated"),
                on_deactivate=body.get_object("on_deactivate"),
                country_modifiers=_collect_objects(body, "country_modifier"),
                province_modifiers=_collect_objects(body, "province_modifier"),
                location_modifiers=_collect_objects(body, "location_modifier"),
                years=parse_int_or_none(body.get_scalar("years")),
                months=parse_int_or_none(body.get_scalar("months")),
                weeks=parse_int_or_none(body.get_scalar("weeks")),
                days=parse_int_or_none(body.get_scalar("days")),
                entry=entry,
            )
        )

    return EstatePrivilegeDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _collect_objects(body: SemanticObject, key: str) -> tuple[SemanticObject, ...]:
    return tuple(
        entry.value
        for entry in body.find_entries(key)
        if isinstance(entry.value, SemanticObject)
    )
