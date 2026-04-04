"""Domain adapter for religion definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
    body_value_text,
    collect_scalar_entries,
    entry_scalar_text,
    object_child_keys,
    parse_bool_or_none,
    parse_float_or_none,
    parse_int_or_none,
)
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ReligionOpinion:
    """One religion-to-religion opinion mapping."""

    religion: str
    stance: str | None
    entry: SemanticEntry


@dataclass(frozen=True)
class ReligionDefinition:
    """One religion definition."""

    name: str
    body: SemanticObject
    group: str | None
    color: str | None
    language: str | None
    enable: str | None
    important_country: str | None
    tithe: float | None
    religious_aspects: int | None
    max_sects: int | None
    ai_wants_convert: bool | None
    has_religious_influence: bool | None
    has_canonization: bool | None
    has_religious_head: bool | None
    has_cardinals: bool | None
    needs_reform: bool | None
    has_karma: bool | None
    has_purity: bool | None
    has_honor: bool | None
    religious_focuses: tuple[str, ...]
    religious_schools: tuple[str, ...]
    num_religious_focuses_needed_for_reform: int | None
    definition_modifier: SemanticObject | None
    opinions: tuple[ReligionOpinion, ...]
    tags: tuple[str, ...]
    custom_tags: tuple[str, ...]
    unique_names: tuple[str, ...]
    factions: tuple[str, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ReligionDocument:
    """Parsed religion file."""

    definitions: tuple[ReligionDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ReligionDefinition | None:
        return get_by_name(self.definitions, name)


def parse_religion_document(text: str) -> ReligionDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ReligionDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        definitions.append(
            ReligionDefinition(
                name=entry.key,
                body=entry.value,
                group=entry.value.get_scalar("group"),
                color=body_value_text(entry.value, "color"),
                language=entry.value.get_scalar("language"),
                enable=entry.value.get_scalar("enable"),
                important_country=entry.value.get_scalar("important_country"),
                tithe=parse_float_or_none(entry.value.get_scalar("tithe")),
                religious_aspects=parse_int_or_none(entry.value.get_scalar("religious_aspects")),
                max_sects=parse_int_or_none(entry.value.get_scalar("max_sects")),
                ai_wants_convert=parse_bool_or_none(entry.value.get_scalar("ai_wants_convert")),
                has_religious_influence=parse_bool_or_none(
                    entry.value.get_scalar("has_religious_influence")
                ),
                has_canonization=parse_bool_or_none(entry.value.get_scalar("has_canonization")),
                has_religious_head=parse_bool_or_none(entry.value.get_scalar("has_religious_head")),
                has_cardinals=parse_bool_or_none(entry.value.get_scalar("has_cardinals")),
                needs_reform=parse_bool_or_none(entry.value.get_scalar("needs_reform")),
                has_karma=parse_bool_or_none(entry.value.get_scalar("has_karma")),
                has_purity=parse_bool_or_none(entry.value.get_scalar("has_purity")),
                has_honor=parse_bool_or_none(entry.value.get_scalar("has_honor")),
                religious_focuses=object_child_keys(entry.value, "religious_focuses"),
                religious_schools=collect_scalar_entries(entry.value, "religious_school"),
                num_religious_focuses_needed_for_reform=parse_int_or_none(
                    entry.value.get_scalar("num_religious_focuses_needed_for_reform")
                ),
                definition_modifier=entry.value.get_object("definition_modifier"),
                opinions=_parse_opinions(entry.value),
                tags=object_child_keys(entry.value, "tags"),
                custom_tags=object_child_keys(entry.value, "custom_tags"),
                unique_names=object_child_keys(entry.value, "unique_names"),
                factions=object_child_keys(entry.value, "factions"),
                entry=entry,
            )
        )

    return ReligionDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_opinions(body: SemanticObject) -> tuple[ReligionOpinion, ...]:
    opinions = body.get_object("opinions")
    if opinions is None:
        return ()

    return tuple(
        ReligionOpinion(
            religion=entry.key,
            stance=entry_scalar_text(entry),
            entry=entry,
        )
        for entry in opinions.entries
    )
