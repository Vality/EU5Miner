"""Domain adapter for parliament issue definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import parse_bool_or_none
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ParliamentIssueDefinition:
    name: str
    body: SemanticObject
    issue_type: str | None
    estates: tuple[str, ...]
    special_statuses: tuple[str, ...]
    show_message: bool | None
    modifier_when_in_debate: SemanticObject | None
    allow: SemanticObject | None
    potential: SemanticObject | None
    selectable_for: SemanticObject | None
    chance: str | SemanticObject | None
    on_debate_passed: SemanticObject | None
    on_debate_failed: SemanticObject | None
    on_debate_start: SemanticObject | None
    wants_this_parliament_issue_bias: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ParliamentIssueDocument:
    definitions: tuple[ParliamentIssueDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ParliamentIssueDefinition | None:
        return get_by_name(self.definitions, name)


def parse_parliament_issue_document(text: str) -> ParliamentIssueDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ParliamentIssueDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            ParliamentIssueDefinition(
                name=entry.key,
                body=body,
                issue_type=body.get_scalar("type"),
                estates=_collect_scalars(body, "estate"),
                special_statuses=_collect_scalars(body, "special_status"),
                show_message=parse_bool_or_none(body.get_scalar("show_message")),
                modifier_when_in_debate=body.get_object("modifier_when_in_debate"),
                allow=body.get_object("allow"),
                potential=body.get_object("potential"),
                selectable_for=body.get_object("selectable_for"),
                chance=_parse_scalar_or_object(body.first_entry("chance")),
                on_debate_passed=body.get_object("on_debate_passed"),
                on_debate_failed=body.get_object("on_debate_failed"),
                on_debate_start=body.get_object("on_debate_start"),
                wants_this_parliament_issue_bias=body.get_object(
                    "wants_this_parliament_issue_bias"
                ),
                entry=entry,
            )
        )

    return ParliamentIssueDocument(
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
