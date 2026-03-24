"""Domain adapter for EU5 disaster definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats import semantic


@dataclass(frozen=True)
class DisasterDefinition:
    """One parsed disaster definition."""

    name: str
    body: semantic.SemanticObject
    image: str | None
    monthly_spawn_chance: str | None
    monthly_spawn_chance_object: semantic.SemanticObject | None
    can_start: semantic.SemanticObject | None
    can_end: semantic.SemanticObject | None
    modifier: semantic.SemanticObject | None
    on_start: semantic.SemanticObject | None
    on_end: semantic.SemanticObject | None
    on_monthly: semantic.SemanticObject | None
    end_trigger_flags: tuple[str, ...]
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class DisasterDocument:
    """Parsed disaster file."""

    definitions: tuple[DisasterDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> DisasterDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_disaster_document(text: str) -> DisasterDocument:
    semantic_document = semantic.parse_semantic_document(text)
    definitions: list[DisasterDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, semantic.SemanticObject):
            continue
        definitions.append(_parse_disaster_definition(entry))

    return DisasterDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_disaster_definition(entry: semantic.SemanticEntry) -> DisasterDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    monthly_spawn_entry = entry.value.first_entry("monthly_spawn_chance")
    end_trigger_flags = tuple(
        child.key
        for child in entry.value.entries
        if child.key.endswith("_end_trigger") and _parse_bool_or_none(_scalar_value(child)) is True
    )

    return DisasterDefinition(
        name=entry.key,
        body=entry.value,
        image=entry.value.get_scalar("image"),
        monthly_spawn_chance=_scalar_value(monthly_spawn_entry),
        monthly_spawn_chance_object=_object_value(monthly_spawn_entry),
        can_start=entry.value.get_object("can_start"),
        can_end=entry.value.get_object("can_end"),
        modifier=entry.value.get_object("modifier"),
        on_start=entry.value.get_object("on_start"),
        on_end=entry.value.get_object("on_end"),
        on_monthly=entry.value.get_object("on_monthly"),
        end_trigger_flags=end_trigger_flags,
        entry=entry,
    )


def _scalar_value(entry: semantic.SemanticEntry | None) -> str | None:
    if entry is None or entry.value is None:
        return None
    if hasattr(entry.value, "text"):
        return entry.value.text
    return None


def _object_value(entry: semantic.SemanticEntry | None) -> semantic.SemanticObject | None:
    if entry is None or not isinstance(entry.value, semantic.SemanticObject):
        return None
    return entry.value


def _parse_bool_or_none(value: str | None) -> bool | None:
    if value is None:
        return None
    if value == "yes":
        return True
    if value == "no":
        return False
    return None