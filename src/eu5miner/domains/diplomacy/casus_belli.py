"""Domain adapter for casus belli definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._parse_helpers import (
    entry_object,
    entry_scalar_text,
    object_child_keys,
    parse_bool_or_none,
)
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class CasusBelliDefinition:
    """One casus belli definition."""

    name: str
    body: SemanticObject
    war_goal_type: str | None
    visible: SemanticObject | None
    allow_creation: SemanticObject | None
    allow_declaration: SemanticObject | None
    province: SemanticObject | None
    ai_will_do: SemanticObject | None
    speed: str | None
    ai_cede_location_desire: str | SemanticObject | None
    ai_subjugation_desire: str | SemanticObject | None
    custom_tags: tuple[str, ...]
    additional_war_enthusiasm: str | None
    additional_war_enthusiasm_attacker: str | None
    additional_war_enthusiasm_defender: str | None
    antagonism_reduction_per_warworth_defender: str | None
    max_warscore_from_battles: str | None
    allow_release_areas: bool | None
    allow_separate_peace: bool | None
    allow_wars_on_own_subjects: bool | None
    allow_ports_for_reach_ai: bool | None
    can_expire: bool | None
    cut_down_in_size_cb: bool | None
    no_cb: bool | None
    trade: bool | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class CasusBelliDocument:
    """Parsed casus belli file."""

    definitions: tuple[CasusBelliDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> CasusBelliDefinition | None:
        return get_by_name(self.definitions, name)


def parse_casus_belli_document(text: str) -> CasusBelliDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[CasusBelliDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            CasusBelliDefinition(
                name=entry.key,
                body=body,
                war_goal_type=body.get_scalar("war_goal_type"),
                visible=body.get_object("visible"),
                allow_creation=body.get_object("allow_creation"),
                allow_declaration=body.get_object("allow_declaration"),
                province=body.get_object("province"),
                ai_will_do=body.get_object("ai_will_do"),
                speed=body.get_scalar("speed"),
                ai_cede_location_desire=_parse_scalar_or_object(
                    body.first_entry("ai_cede_location_desire")
                ),
                ai_subjugation_desire=_parse_scalar_or_object(
                    body.first_entry("ai_subjugation_desire")
                ),
                custom_tags=object_child_keys(body, "custom_tags"),
                additional_war_enthusiasm=body.get_scalar("additional_war_enthusiasm"),
                additional_war_enthusiasm_attacker=body.get_scalar(
                    "additional_war_enthusiasm_attacker"
                ),
                additional_war_enthusiasm_defender=body.get_scalar(
                    "additional_war_enthusiasm_defender"
                ),
                antagonism_reduction_per_warworth_defender=body.get_scalar(
                    "antagonism_reduction_per_warworth_defender"
                ),
                max_warscore_from_battles=body.get_scalar("max_warscore_from_battles"),
                allow_release_areas=parse_bool_or_none(body.get_scalar("allow_release_areas")),
                allow_separate_peace=parse_bool_or_none(
                    body.get_scalar("allow_separate_peace")
                ),
                allow_wars_on_own_subjects=parse_bool_or_none(
                    body.get_scalar("allow_wars_on_own_subjects")
                ),
                allow_ports_for_reach_ai=parse_bool_or_none(
                    body.get_scalar("allow_ports_for_reach_ai")
                ),
                can_expire=parse_bool_or_none(body.get_scalar("can_expire")),
                cut_down_in_size_cb=parse_bool_or_none(
                    body.get_scalar("cut_down_in_size_cb")
                ),
                no_cb=parse_bool_or_none(body.get_scalar("no_cb")),
                trade=parse_bool_or_none(body.get_scalar("trade")),
                entry=entry,
            )
        )

    return CasusBelliDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_scalar_or_object(
    entry: SemanticEntry | None,
) -> str | SemanticObject | None:
    scalar = entry_scalar_text(entry)
    if scalar is not None:
        return scalar
    return entry_object(entry)
