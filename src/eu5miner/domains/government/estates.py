"""Domain adapter for estate definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
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
class EstateDefinition:
    name: str
    body: SemanticObject
    color: str | None
    power_per_pop: int | None
    tax_per_pop: int | None
    rival: float | None
    alliance: float | None
    revolt_court_language: str | None
    priority_for_dynasty_head: bool | None
    can_spawn_random_characters: bool | None
    characters_have_dynasty: str | None
    can_generate_mercenary_leaders: bool | None
    bank: bool | None
    ruler: bool | None
    use_diminutive: bool | None
    satisfaction: SemanticObject | None
    high_power: SemanticObject | None
    low_power: SemanticObject | None
    power: SemanticObject | None
    opinion: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class EstateDocument:
    definitions: tuple[EstateDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> EstateDefinition | None:
        return get_by_name(self.definitions, name)


def parse_estate_document(text: str) -> EstateDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[EstateDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            EstateDefinition(
                name=entry.key,
                body=body,
                color=body.get_scalar("color"),
                power_per_pop=parse_int_or_none(body.get_scalar("power_per_pop")),
                tax_per_pop=parse_int_or_none(body.get_scalar("tax_per_pop")),
                rival=parse_float_or_none(body.get_scalar("rival")),
                alliance=parse_float_or_none(body.get_scalar("alliance")),
                revolt_court_language=body.get_scalar("revolt_court_language"),
                priority_for_dynasty_head=parse_bool_or_none(
                    body.get_scalar("priority_for_dynasty_head")
                ),
                can_spawn_random_characters=parse_bool_or_none(
                    body.get_scalar("can_spawn_random_characters")
                ),
                characters_have_dynasty=body.get_scalar("characters_have_dynasty"),
                can_generate_mercenary_leaders=parse_bool_or_none(
                    body.get_scalar("can_generate_mercenary_leaders")
                ),
                bank=parse_bool_or_none(body.get_scalar("bank")),
                ruler=parse_bool_or_none(body.get_scalar("ruler")),
                use_diminutive=parse_bool_or_none(body.get_scalar("use_diminutive")),
                satisfaction=body.get_object("satisfaction"),
                high_power=body.get_object("high_power"),
                low_power=body.get_object("low_power"),
                power=body.get_object("power"),
                opinion=body.get_object("opinion"),
                entry=entry,
            )
        )

    return EstateDocument(definitions=tuple(definitions), semantic_document=semantic_document)
