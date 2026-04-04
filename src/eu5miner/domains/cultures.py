"""Domain adapter for culture definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
    body_value_text,
    entry_scalar_text,
    object_child_keys,
    parse_bool_or_none,
)
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class CultureOpinion:
    """One culture-to-culture opinion mapping."""

    culture: str
    stance: str | None
    entry: SemanticEntry


@dataclass(frozen=True)
class CultureDefinition:
    """One culture definition."""

    name: str
    body: SemanticObject
    language: str | None
    color: str | None
    tags: tuple[str, ...]
    culture_groups: tuple[str, ...]
    opinions: tuple[CultureOpinion, ...]
    noun_keys: tuple[str, ...]
    adjective_keys: tuple[str, ...]
    use_patronym: bool | None
    dynasty_name_type: str | None
    country_modifier: SemanticObject | None
    character_modifier: SemanticObject | None
    location_modifier: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class CultureDocument:
    """Parsed culture file."""

    definitions: tuple[CultureDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> CultureDefinition | None:
        return get_by_name(self.definitions, name)


def parse_culture_document(text: str) -> CultureDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[CultureDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        definitions.append(
            CultureDefinition(
                name=entry.key,
                body=entry.value,
                language=entry.value.get_scalar("language"),
                color=body_value_text(entry.value, "color"),
                tags=object_child_keys(entry.value, "tags"),
                culture_groups=object_child_keys(entry.value, "culture_groups"),
                opinions=_parse_opinions(entry.value),
                noun_keys=object_child_keys(entry.value, "noun_keys"),
                adjective_keys=object_child_keys(entry.value, "adjective_keys"),
                use_patronym=parse_bool_or_none(entry.value.get_scalar("use_patronym")),
                dynasty_name_type=entry.value.get_scalar("dynasty_name_type"),
                country_modifier=entry.value.get_object("country_modifier"),
                character_modifier=entry.value.get_object("character_modifier"),
                location_modifier=entry.value.get_object("location_modifier"),
                entry=entry,
            )
        )

    return CultureDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_opinions(body: SemanticObject) -> tuple[CultureOpinion, ...]:
    opinions = body.get_object("opinions")
    if opinions is None:
        return ()

    return tuple(
        CultureOpinion(
            culture=entry.key,
            stance=entry_scalar_text(entry),
            entry=entry,
        )
        for entry in opinions.entries
    )
