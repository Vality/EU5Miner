"""Domain adapter for EU5 event definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
    entry_object,
    entry_scalar_text,
    parse_bool_or_none,
)
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class EventOption:
    """One event option block."""

    name: str | None
    body: SemanticObject
    trigger: SemanticObject | None
    hidden_trigger: SemanticObject | None
    ai_chance: SemanticObject | None
    ai_will_select: SemanticObject | None
    historical_option: bool | None
    fallback: bool | None
    exclusive: bool | None
    original_recipient_only: bool | None
    moral_option: bool | None
    evil_option: bool | None
    high_risk_option: bool | None
    high_reward_option: bool | None
    entry: SemanticEntry


@dataclass(frozen=True)
class EventDefinition:
    """One parsed event definition."""

    event_id: str
    namespace: str | None
    event_number: str | None
    body: SemanticObject
    event_type: str | None
    title: str | None
    title_object: SemanticObject | None
    desc: str | None
    desc_object: SemanticObject | None
    historical_info: str | None
    historical_info_object: SemanticObject | None
    image: str | None
    category: str | None
    outcome: str | None
    major: bool | None
    hidden: bool | None
    fire_only_once: bool | None
    interface_lock: bool | None
    orphan: bool | None
    hide_portraits: bool | None
    trigger: SemanticObject | None
    major_trigger: SemanticObject | None
    immediate: SemanticObject | None
    after: SemanticObject | None
    on_trigger_fail: SemanticObject | None
    dynamic_historical_event: SemanticObject | None
    illustration_tags: SemanticObject | None
    weight_multiplier: SemanticObject | None
    options: tuple[EventOption, ...]
    entry: SemanticEntry


@dataclass(frozen=True)
class EventDocument:
    """Parsed event file."""

    namespace: str | None
    definitions: tuple[EventDefinition, ...]
    semantic_document: SemanticDocument

    def event_ids(self) -> tuple[str, ...]:
        return tuple(definition.event_id for definition in self.definitions)

    def get_definition(self, event_id: str) -> EventDefinition | None:
        for definition in self.definitions:
            if definition.event_id == event_id:
                return definition
        return None


def parse_event_document(text: str) -> EventDocument:
    semantic_document = parse_semantic_document(text)
    namespace = semantic_document.first_entry("namespace")
    namespace_text = entry_scalar_text(namespace)
    definitions: list[EventDefinition] = []

    for entry in semantic_document.entries:
        if entry.key == "namespace" or not isinstance(entry.value, SemanticObject):
            continue

        definitions.append(_parse_event_definition(entry, namespace_text))

    return EventDocument(
        namespace=namespace_text,
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_event_definition(
    entry: SemanticEntry,
    document_namespace: str | None,
) -> EventDefinition:
    assert isinstance(entry.value, SemanticObject)

    event_namespace, event_number = _split_event_id(entry.key)
    options = tuple(
        _parse_event_option(option_entry)
        for option_entry in entry.value.find_entries("option")
        if isinstance(option_entry.value, SemanticObject)
    )

    title_entry = entry.value.first_entry("title")
    desc_entry = entry.value.first_entry("desc")
    historical_info_entry = entry.value.first_entry("historical_info")

    return EventDefinition(
        event_id=entry.key,
        namespace=document_namespace or event_namespace,
        event_number=event_number,
        body=entry.value,
        event_type=entry.value.get_scalar("type"),
        title=entry_scalar_text(title_entry),
        title_object=entry_object(title_entry),
        desc=entry_scalar_text(desc_entry),
        desc_object=entry_object(desc_entry),
        historical_info=entry_scalar_text(historical_info_entry),
        historical_info_object=entry_object(historical_info_entry),
        image=entry.value.get_scalar("image"),
        category=entry.value.get_scalar("category"),
        outcome=entry.value.get_scalar("outcome"),
        major=parse_bool_or_none(entry.value.get_scalar("major")),
        hidden=parse_bool_or_none(entry.value.get_scalar("hidden")),
        fire_only_once=parse_bool_or_none(entry.value.get_scalar("fire_only_once")),
        interface_lock=parse_bool_or_none(entry.value.get_scalar("interface_lock")),
        orphan=parse_bool_or_none(entry.value.get_scalar("orphan")),
        hide_portraits=parse_bool_or_none(entry.value.get_scalar("hide_portraits")),
        trigger=entry.value.get_object("trigger"),
        major_trigger=entry.value.get_object("major_trigger"),
        immediate=entry.value.get_object("immediate"),
        after=entry.value.get_object("after"),
        on_trigger_fail=entry.value.get_object("on_trigger_fail"),
        dynamic_historical_event=entry.value.get_object("dynamic_historical_event"),
        illustration_tags=entry.value.get_object("illustration_tags"),
        weight_multiplier=entry.value.get_object("weight_multiplier"),
        options=options,
        entry=entry,
    )


def _parse_event_option(entry: SemanticEntry) -> EventOption:
    assert isinstance(entry.value, SemanticObject)

    return EventOption(
        name=entry.value.get_scalar("name"),
        body=entry.value,
        trigger=entry.value.get_object("trigger"),
        hidden_trigger=entry.value.get_object("hidden_trigger"),
        ai_chance=entry.value.get_object("ai_chance"),
        ai_will_select=entry.value.get_object("ai_will_select"),
        historical_option=parse_bool_or_none(entry.value.get_scalar("historical_option")),
        fallback=parse_bool_or_none(entry.value.get_scalar("fallback")),
        exclusive=parse_bool_or_none(entry.value.get_scalar("exclusive")),
        original_recipient_only=parse_bool_or_none(
            entry.value.get_scalar("original_recipient_only")
        ),
        moral_option=parse_bool_or_none(entry.value.get_scalar("moral_option")),
        evil_option=parse_bool_or_none(entry.value.get_scalar("evil_option")),
        high_risk_option=parse_bool_or_none(entry.value.get_scalar("high_risk_option")),
        high_reward_option=parse_bool_or_none(entry.value.get_scalar("high_reward_option")),
        entry=entry,
    )


def _split_event_id(event_id: str) -> tuple[str | None, str | None]:
    namespace, separator, event_number = event_id.rpartition(".")
    if not separator:
        return None, None
    return namespace or None, event_number or None
