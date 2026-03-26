"""Domain adapter for unit type definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._parse_helpers import (
    entry_object,
    entry_scalar_text,
    object_child_keys,
    parse_bool_or_none,
)
from eu5miner.domains._unit_helpers import UnitModifierValue, collect_unit_modifier_values
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class UnitMercenariesPerLocation:
    pop_type: str | None
    multiply: str | None
    body: SemanticObject
    entry: SemanticEntry


@dataclass(frozen=True)
class UnitTypeDefinition:
    name: str
    body: SemanticObject
    age: str | None
    category: str | None
    copy_from: str | None
    upgrades_to: str | None
    build_time: str | None
    build_time_modifier: str | None
    buildable: bool | None
    levy: bool | None
    light: bool | None
    default: bool | None
    use_ship_names: bool | None
    assault: bool | None
    bombard: bool | None
    auxiliary: bool | None
    is_special: bool | None
    maintenance_demand: str | None
    construction_demand: str | None
    location_trigger: SemanticObject | None
    location_potential: SemanticObject | None
    country_potential: SemanticObject | None
    limit: str | SemanticObject | None
    combat: SemanticObject | None
    impact: SemanticObject | None
    mercenaries_per_location: tuple[UnitMercenariesPerLocation, ...]
    gfx_tags: tuple[str, ...]
    color: str | None
    modifier_values: tuple[UnitModifierValue, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)

    def get_modifier(self, key: str) -> str | None:
        for modifier in self.modifier_values:
            if modifier.key == key:
                return modifier.value
        return None


@dataclass(frozen=True)
class UnitTypeDocument:
    definitions: tuple[UnitTypeDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> UnitTypeDefinition | None:
        return get_by_name(self.definitions, name)


def parse_unit_type_document(text: str) -> UnitTypeDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[UnitTypeDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            UnitTypeDefinition(
                name=entry.key,
                body=body,
                age=body.get_scalar("age"),
                category=body.get_scalar("category"),
                copy_from=body.get_scalar("copy_from"),
                upgrades_to=body.get_scalar("upgrades_to"),
                build_time=body.get_scalar("build_time"),
                build_time_modifier=body.get_scalar("build_time_modifier"),
                buildable=parse_bool_or_none(body.get_scalar("buildable")),
                levy=parse_bool_or_none(body.get_scalar("levy")),
                light=parse_bool_or_none(body.get_scalar("light")),
                default=parse_bool_or_none(body.get_scalar("default")),
                use_ship_names=parse_bool_or_none(body.get_scalar("use_ship_names")),
                assault=parse_bool_or_none(body.get_scalar("assault")),
                bombard=parse_bool_or_none(body.get_scalar("bombard")),
                auxiliary=parse_bool_or_none(body.get_scalar("auxiliary")),
                is_special=parse_bool_or_none(body.get_scalar("is_special")),
                maintenance_demand=body.get_scalar("maintenance_demand"),
                construction_demand=body.get_scalar("construction_demand"),
                location_trigger=body.get_object("location_trigger"),
                location_potential=body.get_object("location_potential"),
                country_potential=body.get_object("country_potential"),
                limit=_parse_scalar_or_object(body.first_entry("limit")),
                combat=body.get_object("combat"),
                impact=body.get_object("impact"),
                mercenaries_per_location=_parse_mercenaries_per_location(body),
                gfx_tags=object_child_keys(body, "gfx_tags"),
                color=body.get_scalar("color"),
                modifier_values=collect_unit_modifier_values(body),
                entry=entry,
            )
        )

    return UnitTypeDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_mercenaries_per_location(
    body: SemanticObject,
) -> tuple[UnitMercenariesPerLocation, ...]:
    values: list[UnitMercenariesPerLocation] = []
    for entry in body.find_entries("mercenaries_per_location"):
        if not isinstance(entry.value, SemanticObject):
            continue
        mercenary_body = entry.value
        values.append(
            UnitMercenariesPerLocation(
                pop_type=mercenary_body.get_scalar("pop_type"),
                multiply=mercenary_body.get_scalar("multiply"),
                body=mercenary_body,
                entry=entry,
            )
        )
    return tuple(values)


def _parse_scalar_or_object(entry: SemanticEntry | None) -> str | SemanticObject | None:
    scalar = entry_scalar_text(entry)
    if scalar is not None:
        return scalar
    return entry_object(entry)
