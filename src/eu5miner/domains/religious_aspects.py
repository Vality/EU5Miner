"""Domain adapter for religious aspect definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._parse_helpers import collect_scalar_entries, entry_scalar_text
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ReligiousAspectOpinion:
    aspect: str
    score: str | None
    entry: SemanticEntry


@dataclass(frozen=True)
class ReligiousAspectDefinition:
    name: str
    body: SemanticObject
    religions: tuple[str, ...]
    visible: SemanticObject | None
    enabled: SemanticObject | None
    modifier: SemanticObject | None
    opinions: tuple[ReligiousAspectOpinion, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ReligiousAspectDocument:
    definitions: tuple[ReligiousAspectDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> ReligiousAspectDefinition | None:
        return get_by_name(self.definitions, name)


def parse_religious_aspect_document(text: str) -> ReligiousAspectDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ReligiousAspectDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            ReligiousAspectDefinition(
                name=entry.key,
                body=body,
                religions=collect_scalar_entries(body, "religion"),
                visible=body.get_object("visible"),
                enabled=body.get_object("enabled"),
                modifier=body.get_object("modifier"),
                opinions=_parse_opinions(body),
                entry=entry,
            )
        )

    return ReligiousAspectDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_opinions(body: SemanticObject) -> tuple[ReligiousAspectOpinion, ...]:
    opinions = body.get_object("opinions")
    if opinions is None:
        return ()

    return tuple(
        ReligiousAspectOpinion(
            aspect=entry.key,
            score=entry_scalar_text(entry),
            entry=entry,
        )
        for entry in opinions.entries
    )
