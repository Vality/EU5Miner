"""Domain adapter for EU5 mission pack definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
    entry_object,
    entry_scalar_text,
    parse_bool_or_none,
    parse_int_or_none,
)
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats import semantic

MISSION_PACK_FIELDS = {
    "header",
    "icon",
    "repeatable",
    "player_playstyle",
    "visible",
    "enabled",
    "abort",
    "chance",
    "ai_will_do",
    "select_trigger",
    "on_potential",
    "on_start",
    "on_abort",
    "on_completion",
    "on_post_completion",
}


@dataclass(frozen=True)
class MissionTaskDefinition:
    """One task within a mission pack."""

    name: str
    body: semantic.SemanticObject
    icon: str | None
    requires: tuple[str, ...]
    final: bool | None
    visible: semantic.SemanticObject | None
    highlight: semantic.SemanticObject | None
    enabled: semantic.SemanticObject | None
    bypass: semantic.SemanticObject | None
    ai_will_do: str | None
    ai_will_do_object: semantic.SemanticObject | None
    duration: int | None
    on_monthly: semantic.SemanticObject | None
    on_start: semantic.SemanticObject | None
    on_persistent_start: semantic.SemanticObject | None
    modifier_while_progressing: semantic.SemanticObject | None
    on_completion: semantic.SemanticObject | None
    on_persistent_completion: semantic.SemanticObject | None
    on_bypass: semantic.SemanticObject | None
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class MissionPackDefinition:
    """One parsed mission pack definition."""

    name: str
    body: semantic.SemanticObject
    header: str | None
    icon: str | None
    repeatable: bool | None
    player_playstyle: str | None
    visible: semantic.SemanticObject | None
    enabled: semantic.SemanticObject | None
    abort: semantic.SemanticObject | None
    chance: str | None
    chance_object: semantic.SemanticObject | None
    ai_will_do: str | None
    ai_will_do_object: semantic.SemanticObject | None
    select_trigger: semantic.SemanticObject | None
    on_potential: semantic.SemanticObject | None
    on_start: semantic.SemanticObject | None
    on_abort: semantic.SemanticObject | None
    on_completion: semantic.SemanticObject | None
    on_post_completion: semantic.SemanticObject | None
    tasks: tuple[MissionTaskDefinition, ...]
    entry: semantic.SemanticEntry

    def task_names(self) -> tuple[str, ...]:
        return names_from_named(self.tasks)

    def get_task(self, name: str) -> MissionTaskDefinition | None:
        return get_by_name(self.tasks, name)


@dataclass(frozen=True)
class MissionDocument:
    """Parsed mission file."""

    definitions: tuple[MissionPackDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> MissionPackDefinition | None:
        return get_by_name(self.definitions, name)


def parse_mission_document(text: str) -> MissionDocument:
    semantic_document = semantic.parse_semantic_document(text)
    definitions: list[MissionPackDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, semantic.SemanticObject):
            continue
        definitions.append(_parse_mission_pack(entry))

    return MissionDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_mission_pack(entry: semantic.SemanticEntry) -> MissionPackDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    chance_entry = entry.value.first_entry("chance")
    ai_will_do_entry = entry.value.first_entry("ai_will_do")
    tasks = tuple(
        _parse_task(task_entry)
        for task_entry in entry.value.entries
        if task_entry.key not in MISSION_PACK_FIELDS
        and isinstance(task_entry.value, semantic.SemanticObject)
    )

    return MissionPackDefinition(
        name=entry.key,
        body=entry.value,
        header=entry.value.get_scalar("header"),
        icon=entry.value.get_scalar("icon"),
        repeatable=parse_bool_or_none(entry.value.get_scalar("repeatable")),
        player_playstyle=entry.value.get_scalar("player_playstyle"),
        visible=entry.value.get_object("visible"),
        enabled=entry.value.get_object("enabled"),
        abort=entry.value.get_object("abort"),
        chance=entry_scalar_text(chance_entry),
        chance_object=entry_object(chance_entry),
        ai_will_do=entry_scalar_text(ai_will_do_entry),
        ai_will_do_object=entry_object(ai_will_do_entry),
        select_trigger=entry.value.get_object("select_trigger"),
        on_potential=entry.value.get_object("on_potential"),
        on_start=entry.value.get_object("on_start"),
        on_abort=entry.value.get_object("on_abort"),
        on_completion=entry.value.get_object("on_completion"),
        on_post_completion=entry.value.get_object("on_post_completion"),
        tasks=tasks,
        entry=entry,
    )


def _parse_task(entry: semantic.SemanticEntry) -> MissionTaskDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    ai_will_do_entry = entry.value.first_entry("ai_will_do")

    return MissionTaskDefinition(
        name=entry.key,
        body=entry.value,
        icon=entry.value.get_scalar("icon"),
        requires=_extract_list_names(entry.value.get_object("requires")),
        final=parse_bool_or_none(entry.value.get_scalar("final")),
        visible=entry.value.get_object("visible"),
        highlight=entry.value.get_object("highlight"),
        enabled=entry.value.get_object("enabled"),
        bypass=entry.value.get_object("bypass"),
        ai_will_do=entry_scalar_text(ai_will_do_entry),
        ai_will_do_object=entry_object(ai_will_do_entry),
        duration=parse_int_or_none(entry.value.get_scalar("duration")),
        on_monthly=entry.value.get_object("on_monthly"),
        on_start=entry.value.get_object("on_start"),
        on_persistent_start=entry.value.get_object("on_persistent_start"),
        modifier_while_progressing=entry.value.get_object("modifier_while_progressing"),
        on_completion=entry.value.get_object("on_completion"),
        on_persistent_completion=entry.value.get_object("on_persistent_completion"),
        on_bypass=entry.value.get_object("on_bypass"),
        entry=entry,
    )


def _extract_list_names(value: semantic.SemanticObject | None) -> tuple[str, ...]:
    if value is None:
        return ()
    return tuple(entry.key for entry in value.entries)
