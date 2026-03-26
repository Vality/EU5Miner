"""Domain adapter for unit ability definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._parse_helpers import parse_bool_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class UnitAbilityDefinition:
    name: str
    body: SemanticObject
    hidden: SemanticObject | None
    allow: SemanticObject | None
    finished_when: SemanticObject | None
    ai_will_revoke: SemanticObject | None
    ai_allow_plan_slowdown: bool | None
    duration: str | None
    toggle: bool | None
    soundeffect: str | None
    army_only: bool | None
    navy_only: bool | None
    cancel_on_combat: bool | None
    cancel_on_combat_end: bool | None
    cancel_on_move: bool | None
    map: bool | None
    start_effect: SemanticObject | None
    finish_effect: SemanticObject | None
    on_entering_location: SemanticObject | None
    ai_will_do: SemanticObject | None
    modifier: SemanticObject | None
    idle_entity_state: str | None
    move_entity_state: str | None
    available_states: SemanticObject | None
    confirm: bool | None
    block_reorg: bool | None
    animation_gfx_override: str | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class UnitAbilityDocument:
    definitions: tuple[UnitAbilityDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> UnitAbilityDefinition | None:
        return get_by_name(self.definitions, name)


def parse_unit_ability_document(text: str) -> UnitAbilityDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[UnitAbilityDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            UnitAbilityDefinition(
                name=entry.key,
                body=body,
                hidden=body.get_object("hidden"),
                allow=body.get_object("allow"),
                finished_when=body.get_object("finished_when"),
                ai_will_revoke=body.get_object("ai_will_revoke"),
                ai_allow_plan_slowdown=parse_bool_or_none(
                    body.get_scalar("ai_allow_plan_slowdown")
                ),
                duration=body.get_scalar("duration"),
                toggle=parse_bool_or_none(body.get_scalar("toggle")),
                soundeffect=body.get_scalar("soundeffect"),
                army_only=parse_bool_or_none(body.get_scalar("army_only")),
                navy_only=parse_bool_or_none(body.get_scalar("navy_only")),
                cancel_on_combat=parse_bool_or_none(body.get_scalar("cancel_on_combat")),
                cancel_on_combat_end=parse_bool_or_none(
                    body.get_scalar("cancel_on_combat_end")
                ),
                cancel_on_move=parse_bool_or_none(body.get_scalar("cancel_on_move")),
                map=parse_bool_or_none(body.get_scalar("map")),
                start_effect=body.get_object("start_effect"),
                finish_effect=body.get_object("finish_effect"),
                on_entering_location=body.get_object("on_entering_location"),
                ai_will_do=body.get_object("ai_will_do"),
                modifier=body.get_object("modifier"),
                idle_entity_state=body.get_scalar("idle_entity_state"),
                move_entity_state=body.get_scalar("move_entity_state"),
                available_states=body.get_object("available_states"),
                confirm=parse_bool_or_none(body.get_scalar("confirm")),
                block_reorg=parse_bool_or_none(body.get_scalar("block_reorg")),
                animation_gfx_override=body.get_scalar("animation_gfx_override"),
                entry=entry,
            )
        )

    return UnitAbilityDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
