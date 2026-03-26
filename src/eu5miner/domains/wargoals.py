"""Domain adapter for war goal definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import entry_object, parse_bool_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class WargoalParticipantDefinition:
    """One participant-side rules block within a war goal."""

    body: SemanticObject
    call_in_overlord: bool | None
    call_in_subjects: bool | None
    conquer_cost: str | None
    subjugate_cost: str | None
    antagonism: str | None
    allowed_locations: SemanticObject | None
    allowed_subjugation: SemanticObject | None
    entry: SemanticEntry


@dataclass(frozen=True)
class WargoalDefinition:
    """One war goal definition."""

    name: str
    body: SemanticObject
    war_goal_type: str | None
    war_name: str | None
    war_name_is_country_order_agnostic: bool | None
    attacker: WargoalParticipantDefinition | None
    defender: WargoalParticipantDefinition | None
    ticking_war_score: str | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class WargoalDocument:
    """Parsed war goal file."""

    definitions: tuple[WargoalDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> WargoalDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_wargoal_document(text: str) -> WargoalDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[WargoalDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            WargoalDefinition(
                name=entry.key,
                body=body,
                war_goal_type=body.get_scalar("type"),
                war_name=body.get_scalar("war_name"),
                war_name_is_country_order_agnostic=parse_bool_or_none(
                    body.get_scalar("war_name_is_country_order_agnostic")
                ),
                attacker=_parse_participant(body.first_entry("attacker")),
                defender=_parse_participant(body.first_entry("defender")),
                ticking_war_score=body.get_scalar("ticking_war_score"),
                entry=entry,
            )
        )

    return WargoalDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_participant(entry: SemanticEntry | None) -> WargoalParticipantDefinition | None:
    body = entry_object(entry)
    if body is None or entry is None:
        return None

    return WargoalParticipantDefinition(
        body=body,
        call_in_overlord=parse_bool_or_none(body.get_scalar("call_in_overlord")),
        call_in_subjects=parse_bool_or_none(body.get_scalar("call_in_subjects")),
        conquer_cost=body.get_scalar("conquer_cost"),
        subjugate_cost=body.get_scalar("subjugate_cost"),
        antagonism=body.get_scalar("antagonism"),
        allowed_locations=body.get_object("allowed_locations"),
        allowed_subjugation=body.get_object("allowed_subjugation"),
        entry=entry,
    )