"""Domain adapter for unit category definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import parse_bool_or_none, parse_float_or_none, parse_int_or_none
from eu5miner.domains._unit_helpers import UnitModifierValue, collect_unit_modifier_values
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class UnitCategoryDefinition:
    name: str
    body: SemanticObject
    startup_amount: int | None
    build_time: str | None
    assault: bool | None
    bombard: bool | None
    auxiliary: bool | None
    is_garrison: bool | None
    is_army: bool | None
    transport: bool | None
    construction_demand: str | None
    maintenance_demand: str | None
    combat: SemanticObject | None
    ai_weight: float | None
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
class UnitCategoryDocument:
    definitions: tuple[UnitCategoryDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> UnitCategoryDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_unit_category_document(text: str) -> UnitCategoryDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[UnitCategoryDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            UnitCategoryDefinition(
                name=entry.key,
                body=body,
                startup_amount=parse_int_or_none(body.get_scalar("startup_amount")),
                build_time=body.get_scalar("build_time"),
                assault=parse_bool_or_none(body.get_scalar("assault")),
                bombard=parse_bool_or_none(body.get_scalar("bombard")),
                auxiliary=parse_bool_or_none(body.get_scalar("auxiliary")),
                is_garrison=parse_bool_or_none(body.get_scalar("is_garrison")),
                is_army=parse_bool_or_none(body.get_scalar("is_army")),
                transport=parse_bool_or_none(body.get_scalar("transport")),
                construction_demand=body.get_scalar("construction_demand"),
                maintenance_demand=body.get_scalar("maintenance_demand"),
                combat=body.get_object("combat"),
                ai_weight=parse_float_or_none(body.get_scalar("ai_weight")),
                modifier_values=collect_unit_modifier_values(body),
                entry=entry,
            )
        )

    return UnitCategoryDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
