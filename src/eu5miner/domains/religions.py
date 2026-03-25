"""Domain adapter for religion definitions."""

from __future__ import annotations

from dataclasses import dataclass

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
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> ReligionDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


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
                color=_get_value_text(entry.value, "color"),
                language=entry.value.get_scalar("language"),
                enable=entry.value.get_scalar("enable"),
                important_country=entry.value.get_scalar("important_country"),
                tithe=_parse_float_or_none(entry.value.get_scalar("tithe")),
                religious_aspects=_parse_int_or_none(
                    entry.value.get_scalar("religious_aspects")
                ),
                max_sects=_parse_int_or_none(entry.value.get_scalar("max_sects")),
                ai_wants_convert=_parse_bool_or_none(
                    entry.value.get_scalar("ai_wants_convert")
                ),
                has_religious_influence=_parse_bool_or_none(
                    entry.value.get_scalar("has_religious_influence")
                ),
                has_canonization=_parse_bool_or_none(
                    entry.value.get_scalar("has_canonization")
                ),
                has_religious_head=_parse_bool_or_none(
                    entry.value.get_scalar("has_religious_head")
                ),
                has_cardinals=_parse_bool_or_none(entry.value.get_scalar("has_cardinals")),
                needs_reform=_parse_bool_or_none(entry.value.get_scalar("needs_reform")),
                has_karma=_parse_bool_or_none(entry.value.get_scalar("has_karma")),
                has_purity=_parse_bool_or_none(entry.value.get_scalar("has_purity")),
                has_honor=_parse_bool_or_none(entry.value.get_scalar("has_honor")),
                definition_modifier=entry.value.get_object("definition_modifier"),
                opinions=_parse_opinions(entry.value),
                tags=_get_name_list(entry.value, "tags"),
                custom_tags=_get_name_list(entry.value, "custom_tags"),
                unique_names=_get_name_list(entry.value, "unique_names"),
                factions=_get_name_list(entry.value, "factions"),
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
            stance=_scalar_value(entry),
            entry=entry,
        )
        for entry in opinions.entries
    )


def _get_name_list(body: SemanticObject, key: str) -> tuple[str, ...]:
    value = body.get_object(key)
    if value is None:
        return ()
    return tuple(entry.key for entry in value.entries)


def _scalar_value(entry: SemanticEntry | None) -> str | None:
    if entry is None or entry.value is None:
        return None
    if hasattr(entry.value, "text"):
        return entry.value.text
    return None


def _parse_bool_or_none(value: str | None) -> bool | None:
    if value == "yes":
        return True
    if value == "no":
        return False
    return None


def _parse_float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _parse_int_or_none(value: str | None) -> int | None:
    if value is None:
        return None
    return int(value)


def _get_value_text(body: SemanticObject, key: str) -> str | None:
    entry = body.first_entry(key)
    if entry is None or entry.value is None:
        return None
    if hasattr(entry.value, "text"):
        return entry.value.text
    if isinstance(entry.value, SemanticObject):
        return entry.value.prefix or None
    return None
