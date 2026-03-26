"""Domain adapter for subject military stance definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import parse_bool_or_none, parse_float_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class SubjectMilitaryStanceDefinition:
    """One subject military stance definition."""

    name: str
    body: SemanticObject
    is_default: bool | None
    chase_unit_own_location_priority: float | None
    chase_unit_overlord_location_priority: float | None
    chase_unit_subject_location_priority: float | None
    chase_unit_friendly_location_priority: float | None
    chase_unit_neutral_location_priority: float | None
    chase_unit_enemy_location_priority: float | None
    chase_navy_priority: float | None
    hunt_army_priority: float | None
    hunt_navy_priority: float | None
    defend_own_territory_priority: float | None
    defend_ally_territory_priority: float | None
    merge_units_priority: float | None
    hunt_pirates_priority: float | None
    repatriate_ships_priority: float | None
    repatriate_troops_priority: float | None
    support_armies_priority: float | None
    support_sieges_priority: float | None
    maintain_military_levels_priority: float | None
    carpet_siege_own_locations_attacking_priority: float | None
    carpet_siege_own_locations_defending_priority: float | None
    carpet_siege_enemy_locations_priority: float | None
    blockade_port_priority: float | None
    blockade_strait_priority: float | None
    suppress_rebel_priority: float | None
    army_logistics_priority: float | None
    navy_logistics_priority: float | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class SubjectMilitaryStanceDocument:
    """Parsed subject military stance file."""

    definitions: tuple[SubjectMilitaryStanceDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> SubjectMilitaryStanceDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_subject_military_stance_document(text: str) -> SubjectMilitaryStanceDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[SubjectMilitaryStanceDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            SubjectMilitaryStanceDefinition(
                name=entry.key,
                body=body,
                is_default=parse_bool_or_none(body.get_scalar("is_default")),
                chase_unit_own_location_priority=parse_float_or_none(
                    body.get_scalar("chase_unit_own_location_priority")
                ),
                chase_unit_overlord_location_priority=parse_float_or_none(
                    body.get_scalar("chase_unit_overlord_location_priority")
                ),
                chase_unit_subject_location_priority=parse_float_or_none(
                    body.get_scalar("chase_unit_subject_location_priority")
                ),
                chase_unit_friendly_location_priority=parse_float_or_none(
                    body.get_scalar("chase_unit_friendly_location_priority")
                ),
                chase_unit_neutral_location_priority=parse_float_or_none(
                    body.get_scalar("chase_unit_neutral_location_priority")
                ),
                chase_unit_enemy_location_priority=parse_float_or_none(
                    body.get_scalar("chase_unit_enemy_location_priority")
                ),
                chase_navy_priority=parse_float_or_none(body.get_scalar("chase_navy_priority")),
                hunt_army_priority=parse_float_or_none(body.get_scalar("hunt_army_priority")),
                hunt_navy_priority=parse_float_or_none(body.get_scalar("hunt_navy_priority")),
                defend_own_territory_priority=parse_float_or_none(
                    body.get_scalar("defend_own_territory_priority")
                ),
                defend_ally_territory_priority=parse_float_or_none(
                    body.get_scalar("defend_ally_territory_priority")
                ),
                merge_units_priority=parse_float_or_none(body.get_scalar("merge_units_priority")),
                hunt_pirates_priority=parse_float_or_none(
                    body.get_scalar("hunt_pirates_priority")
                ),
                repatriate_ships_priority=parse_float_or_none(
                    body.get_scalar("repatriate_ships_priority")
                ),
                repatriate_troops_priority=parse_float_or_none(
                    body.get_scalar("repatriate_troops_priority")
                ),
                support_armies_priority=parse_float_or_none(
                    body.get_scalar("support_armies_priority")
                ),
                support_sieges_priority=parse_float_or_none(
                    body.get_scalar("support_sieges_priority")
                ),
                maintain_military_levels_priority=parse_float_or_none(
                    body.get_scalar("maintain_military_levels_priority")
                ),
                carpet_siege_own_locations_attacking_priority=parse_float_or_none(
                    body.get_scalar("carpet_siege_own_locations_attacking_priority")
                ),
                carpet_siege_own_locations_defending_priority=parse_float_or_none(
                    body.get_scalar("carpet_siege_own_locations_defending_priority")
                ),
                carpet_siege_enemy_locations_priority=parse_float_or_none(
                    body.get_scalar("carpet_siege_enemy_locations_priority")
                ),
                blockade_port_priority=parse_float_or_none(body.get_scalar("blockade_port_priority")),
                blockade_strait_priority=parse_float_or_none(
                    body.get_scalar("blockade_strait_priority")
                ),
                suppress_rebel_priority=parse_float_or_none(
                    body.get_scalar("suppress_rebel_priority")
                ),
                army_logistics_priority=parse_float_or_none(
                    body.get_scalar("army_logistics_priority")
                ),
                navy_logistics_priority=parse_float_or_none(
                    body.get_scalar("navy_logistics_priority")
                ),
                entry=entry,
            )
        )

    return SubjectMilitaryStanceDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
