"""Domain adapter for EU5 situation definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import entry_object, entry_scalar_text, parse_bool_or_none
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats import semantic


@dataclass(frozen=True)
class SituationDefinition:
    """One parsed situation definition."""

    name: str
    body: semantic.SemanticObject
    monthly_spawn_chance: str | None
    monthly_spawn_chance_object: semantic.SemanticObject | None
    international_organization_type: str | None
    resolution: str | None
    voters: str | None
    hint_tag: str | None
    can_start: semantic.SemanticObject | None
    can_end: semantic.SemanticObject | None
    visible: semantic.SemanticObject | None
    on_start: semantic.SemanticObject | None
    on_monthly: semantic.SemanticObject | None
    on_ending: semantic.SemanticObject | None
    on_ended: semantic.SemanticObject | None
    tooltip: semantic.SemanticObject | None
    map_color: semantic.SemanticObject | None
    secondary_map_color: semantic.SemanticObject | None
    is_data_map: bool | None
    end_trigger_flags: tuple[str, ...]
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class SituationDocument:
    """Parsed situation file."""

    definitions: tuple[SituationDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> SituationDefinition | None:
        return get_by_name(self.definitions, name)


def parse_situation_document(text: str) -> SituationDocument:
    semantic_document = semantic.parse_semantic_document(text)
    definitions: list[SituationDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, semantic.SemanticObject):
            continue
        definitions.append(_parse_situation_definition(entry))

    return SituationDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_situation_definition(entry: semantic.SemanticEntry) -> SituationDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    monthly_spawn_entry = entry.value.first_entry("monthly_spawn_chance")
    end_trigger_flags = tuple(
        child.key
        for child in entry.value.entries
        if child.key.endswith("_end_trigger")
        and parse_bool_or_none(entry_scalar_text(child)) is True
    )

    return SituationDefinition(
        name=entry.key,
        body=entry.value,
        monthly_spawn_chance=entry_scalar_text(monthly_spawn_entry),
        monthly_spawn_chance_object=entry_object(monthly_spawn_entry),
        international_organization_type=entry.value.get_scalar("international_organization_type"),
        resolution=entry.value.get_scalar("resolution"),
        voters=entry.value.get_scalar("voters"),
        hint_tag=entry.value.get_scalar("hint_tag"),
        can_start=entry.value.get_object("can_start"),
        can_end=entry.value.get_object("can_end"),
        visible=entry.value.get_object("visible"),
        on_start=entry.value.get_object("on_start"),
        on_monthly=entry.value.get_object("on_monthly"),
        on_ending=entry.value.get_object("on_ending"),
        on_ended=entry.value.get_object("on_ended"),
        tooltip=entry.value.get_object("tooltip"),
        map_color=entry.value.get_object("map_color"),
        secondary_map_color=entry.value.get_object("secondary_map_color"),
        is_data_map=parse_bool_or_none(entry.value.get_scalar("is_data_map")),
        end_trigger_flags=end_trigger_flags,
        entry=entry,
    )
