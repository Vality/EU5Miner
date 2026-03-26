"""Domain adapter for parliament agenda definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ParliamentAgendaDefinition:
    name: str
    body: SemanticObject
    agenda_type: str | None
    estates: tuple[str, ...]
    special_statuses: tuple[str, ...]
    potential: SemanticObject | None
    allow: SemanticObject | None
    on_accept: SemanticObject | None
    on_bribe: SemanticObject | None
    can_bribe: SemanticObject | None
    ai_will_do: SemanticObject | None
    chance: str | SemanticObject | None
    importance: str | SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ParliamentAgendaDocument:
    definitions: tuple[ParliamentAgendaDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ParliamentAgendaDefinition | None:
        return get_by_name(self.definitions, name)


def parse_parliament_agenda_document(text: str) -> ParliamentAgendaDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ParliamentAgendaDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            ParliamentAgendaDefinition(
                name=entry.key,
                body=body,
                agenda_type=body.get_scalar("type"),
                estates=_collect_scalars(body, "estate"),
                special_statuses=_collect_scalars(body, "special_status"),
                potential=body.get_object("potential"),
                allow=body.get_object("allow"),
                on_accept=body.get_object("on_accept"),
                on_bribe=body.get_object("on_bribe"),
                can_bribe=body.get_object("can_bribe"),
                ai_will_do=body.get_object("ai_will_do"),
                chance=_parse_scalar_or_object(body.first_entry("chance")),
                importance=_parse_scalar_or_object(body.first_entry("importance")),
                entry=entry,
            )
        )

    return ParliamentAgendaDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _collect_scalars(body: SemanticObject, key: str) -> tuple[str, ...]:
    return tuple(
        entry.value.text
        for entry in body.find_entries(key)
        if isinstance(entry.value, SemanticScalar)
    )


def _parse_scalar_or_object(entry: SemanticEntry | None) -> str | SemanticObject | None:
    if entry is None:
        return None
    if isinstance(entry.value, SemanticScalar):
        return entry.value.text
    if isinstance(entry.value, SemanticObject):
        return entry.value
    return None
