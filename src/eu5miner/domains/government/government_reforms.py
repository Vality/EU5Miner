"""Domain adapter for government reform definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._parse_helpers import object_child_keys, parse_bool_or_none, parse_int_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class GovernmentReformDefinition:
    name: str
    body: SemanticObject
    age: str | None
    government: str | None
    major: bool | None
    unique: bool | None
    block_for_rebel: bool | None
    icon: str | None
    societal_values: tuple[str, ...]
    male_regnal_names: tuple[str, ...]
    female_regnal_names: tuple[str, ...]
    potential: SemanticObject | None
    allow: SemanticObject | None
    locked: SemanticObject | None
    on_activate: SemanticObject | None
    on_fully_activated: SemanticObject | None
    on_deactivate: SemanticObject | None
    country_modifier: SemanticObject | None
    province_modifier: SemanticObject | None
    location_modifier: SemanticObject | None
    years: int | None
    months: int | None
    weeks: int | None
    days: int | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class GovernmentReformDocument:
    definitions: tuple[GovernmentReformDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> GovernmentReformDefinition | None:
        return get_by_name(self.definitions, name)


def parse_government_reform_document(text: str) -> GovernmentReformDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[GovernmentReformDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            GovernmentReformDefinition(
                name=entry.key,
                body=body,
                age=body.get_scalar("age"),
                government=body.get_scalar("government"),
                major=parse_bool_or_none(body.get_scalar("major")),
                unique=parse_bool_or_none(body.get_scalar("unique")),
                block_for_rebel=parse_bool_or_none(body.get_scalar("block_for_rebel")),
                icon=body.get_scalar("icon"),
                societal_values=object_child_keys(body, "societal_values"),
                male_regnal_names=object_child_keys(body, "male_regnal_names"),
                female_regnal_names=object_child_keys(body, "female_regnal_names"),
                potential=body.get_object("potential"),
                allow=body.get_object("allow"),
                locked=body.get_object("locked"),
                on_activate=body.get_object("on_activate"),
                on_fully_activated=body.get_object("on_fully_activated"),
                on_deactivate=body.get_object("on_deactivate"),
                country_modifier=body.get_object("country_modifier"),
                province_modifier=body.get_object("province_modifier"),
                location_modifier=body.get_object("location_modifier"),
                years=parse_int_or_none(body.get_scalar("years")),
                months=parse_int_or_none(body.get_scalar("months")),
                weeks=parse_int_or_none(body.get_scalar("weeks")),
                days=parse_int_or_none(body.get_scalar("days")),
                entry=entry,
            )
        )

    return GovernmentReformDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
