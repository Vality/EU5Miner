"""Shared helpers for unit-related domain adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from eu5miner.domains._parse_helpers import entry_scalar_text
from eu5miner.formats.semantic import SemanticEntry, SemanticObject

UNIT_MODIFIER_KEYS = frozenset(
    {
        "anti_piracy_warfare",
        "artillery_barrage",
        "attrition_loss",
        "blockade_capacity",
        "bombard_efficiency",
        "cannons",
        "combat_power",
        "combat_speed",
        "crew_size",
        "damage_taken",
        "flanking_ability",
        "food_consumption_per_strength",
        "food_storage_per_strength",
        "frontage",
        "hull_size",
        "initiative",
        "maritime_presence",
        "max_strength",
        "morale_damage_done",
        "morale_damage_taken",
        "movement_speed",
        "secure_flanks_defense",
        "strength_damage_done",
        "strength_damage_taken",
        "supply_weight",
        "transport_capacity",
    }
)


@dataclass(frozen=True)
class UnitModifierValue:
    key: str
    value: str
    entry: SemanticEntry


@runtime_checkable
class UnitModifierBearingLike(Protocol):
    @property
    def modifier_values(self) -> tuple[UnitModifierValue, ...]: ...


def collect_unit_modifier_values(body: SemanticObject) -> tuple[UnitModifierValue, ...]:
    values: list[UnitModifierValue] = []
    for entry in body.entries:
        if entry.key not in UNIT_MODIFIER_KEYS:
            continue
        scalar = entry_scalar_text(entry)
        if scalar is None:
            continue
        values.append(UnitModifierValue(key=entry.key, value=scalar, entry=entry))
    return tuple(values)


def get_unit_modifier(definition: UnitModifierBearingLike, key: str) -> str | None:
    for modifier in definition.modifier_values:
        if modifier.key == key:
            return modifier.value
    return None
