"""Domain adapter for on_action definitions and related documentation."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from eu5miner.domains._macros import collect_parameters_from_object
from eu5miner.domains._parse_helpers import parse_int_or_none
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)

_DOC_SEPARATOR_RE = re.compile(r"\n-{10,}\n")


@dataclass(frozen=True)
class OnActionReference:
    """One plain named reference inside an on_action block."""

    name: str
    entry: SemanticEntry


@dataclass(frozen=True)
class OnActionRandomEvent:
    """One weighted random event reference."""

    weight: int
    event: str
    entry: SemanticEntry


@dataclass(frozen=True)
class OnActionRandomEvents:
    """Parsed random_events block contents."""

    weighted_events: tuple[OnActionRandomEvent, ...]
    chance_to_happen: str | None
    chance_of_no_event: SemanticObject | None
    body: SemanticObject


@dataclass(frozen=True)
class OnActionDefinition:
    """One on_action definition."""

    name: str
    body: SemanticObject
    trigger: SemanticObject | None
    effect: SemanticObject | None
    events: tuple[OnActionReference, ...]
    on_actions: tuple[OnActionReference, ...]
    random_events: OnActionRandomEvents | None
    parameters: tuple[str, ...]
    entry: SemanticEntry


@dataclass(frozen=True)
class OnActionDocument:
    """Parsed on_action file."""

    definitions: tuple[OnActionDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> OnActionDefinition | None:
        return get_by_name(self.definitions, name)


@dataclass(frozen=True)
class OnActionDocumentationDefinition:
    """One documented hook from the generated on_actions dump."""

    name: str
    from_code: bool | None
    expected_scope: str | None


@dataclass(frozen=True)
class OnActionDocumentationDocument:
    """Parsed generated on_action documentation dump."""

    definitions: tuple[OnActionDocumentationDefinition, ...]

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> OnActionDocumentationDefinition | None:
        return get_by_name(self.definitions, name)


@dataclass(frozen=True)
class OnActionCatalogEntry:
    """Cross-linked view of one on_action name across files and docs."""

    name: str
    definitions: tuple[OnActionDefinition, ...]
    documentation: OnActionDocumentationDefinition | None


@dataclass(frozen=True)
class OnActionCatalogDocument:
    """Merged catalog for on_action definitions and documentation."""

    entries: tuple[OnActionCatalogEntry, ...]

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.entries)

    def get_entry(self, name: str) -> OnActionCatalogEntry | None:
        return get_by_name(self.entries, name)

    def get_definition(self, name: str) -> OnActionCatalogEntry | None:
        return self.get_entry(name)


def parse_on_action_document(text: str) -> OnActionDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[OnActionDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            OnActionDefinition(
                name=entry.key,
                body=body,
                trigger=body.get_object("trigger"),
                effect=body.get_object("effect"),
                events=_collect_named_references(body.get_object("events")),
                on_actions=_collect_named_references(body.get_object("on_actions")),
                random_events=_parse_random_events(body.get_object("random_events")),
                parameters=tuple(sorted(collect_parameters_from_object(body))),
                entry=entry,
            )
        )

    return OnActionDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def parse_on_action_documentation(text: str) -> OnActionDocumentationDocument:
    normalized_text = text.replace("\r\n", "\n")
    definitions: list[OnActionDocumentationDefinition] = []

    for section in _DOC_SEPARATOR_RE.split(normalized_text):
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        if not lines or lines[0] == "On Action Documentation:":
            continue

        header = lines[0]
        if not header.endswith(":"):
            continue

        from_code: bool | None = None
        expected_scope: str | None = None
        for line in lines[1:]:
            if line.startswith("From Code:"):
                from_code_text = line.removeprefix("From Code:").strip()
                if from_code_text == "Yes":
                    from_code = True
                elif from_code_text == "No":
                    from_code = False
            if line.startswith("Expected Scope:"):
                expected_scope = line.removeprefix("Expected Scope:").strip() or None

        definitions.append(
            OnActionDocumentationDefinition(
                name=header.removesuffix(":"),
                from_code=from_code,
                expected_scope=expected_scope,
            )
        )

    return OnActionDocumentationDocument(definitions=tuple(definitions))


def build_on_action_catalog_document(
    documents: Iterable[OnActionDocument],
    documentation_document: OnActionDocumentationDocument | None = None,
) -> OnActionCatalogDocument:
    definitions_by_name: dict[str, list[OnActionDefinition]] = defaultdict(list)
    documentation_by_name: dict[str, OnActionDocumentationDefinition] = {}

    for document in documents:
        for definition in document.definitions:
            definitions_by_name[definition.name].append(definition)

    if documentation_document is not None:
        documentation_by_name = {
            definition.name: definition for definition in documentation_document.definitions
        }

    names = sorted(set(definitions_by_name) | set(documentation_by_name))
    entries = tuple(
        OnActionCatalogEntry(
            name=name,
            definitions=tuple(definitions_by_name.get(name, ())),
            documentation=documentation_by_name.get(name),
        )
        for name in names
    )
    return OnActionCatalogDocument(entries=entries)


def _collect_named_references(block: SemanticObject | None) -> tuple[OnActionReference, ...]:
    if block is None:
        return ()

    references: list[OnActionReference] = []
    for entry in block.entries:
        if entry.operator is None and entry.value is None:
            references.append(OnActionReference(name=entry.key, entry=entry))
            continue

        if isinstance(entry.value, SemanticScalar):
            references.append(OnActionReference(name=entry.value.text, entry=entry))

    return tuple(references)


def _parse_random_events(block: SemanticObject | None) -> OnActionRandomEvents | None:
    if block is None:
        return None

    weighted_events: list[OnActionRandomEvent] = []
    for entry in block.entries:
        if not isinstance(entry.value, SemanticScalar):
            continue

        weight = parse_int_or_none(entry.key)
        if weight is None:
            continue

        weighted_events.append(
            OnActionRandomEvent(weight=weight, event=entry.value.text, entry=entry)
        )

    return OnActionRandomEvents(
        weighted_events=tuple(weighted_events),
        chance_to_happen=block.get_scalar("chance_to_happen"),
        chance_of_no_event=block.get_object("chance_of_no_event"),
        body=block,
    )
