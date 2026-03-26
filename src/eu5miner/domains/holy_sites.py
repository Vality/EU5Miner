"""Domain adapter and catalog helpers for holy site definitions."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from eu5miner.domains.interfaces import flatten_definitions, get_by_name, get_scalar_from_body, names_from_named
from eu5miner.domains._parse_helpers import object_child_keys, parse_int_or_none
from eu5miner.domains.holy_site_types import HolySiteTypeDefinition, HolySiteTypeDocument
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class HolySiteDefinition:
    name: str
    body: SemanticObject
    location: str | None
    holy_site_type: str | None
    importance: int | None
    religions: tuple[str, ...]
    god: str | None
    avatar: str | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return get_scalar_from_body(self, key)


@dataclass(frozen=True)
class HolySiteDocument:
    definitions: tuple[HolySiteDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> HolySiteDefinition | None:
        return get_by_name(self.definitions, name)


@dataclass(frozen=True)
class HolySiteReferenceEdge:
    source_name: str
    referenced_names: tuple[str, ...]


@dataclass(frozen=True)
class HolySiteReport:
    holy_site_type_links: tuple[HolySiteReferenceEdge, ...]
    missing_holy_site_type_references: tuple[str, ...]


@dataclass(frozen=True)
class HolySiteCatalog:
    holy_site_type_definitions: tuple[HolySiteTypeDefinition, ...]
    holy_site_definitions: tuple[HolySiteDefinition, ...]

    def get_holy_site_type(self, name: str) -> HolySiteTypeDefinition | None:
        return get_by_name(self.holy_site_type_definitions, name)

    def get_holy_site(self, name: str) -> HolySiteDefinition | None:
        return get_by_name(self.holy_site_definitions, name)

    def get_holy_sites_for_type(self, type_name: str) -> tuple[HolySiteDefinition, ...]:
        return tuple(
            definition
            for definition in self.holy_site_definitions
            if definition.holy_site_type == type_name
        )

    def get_holy_sites_for_religion(self, religion_name: str) -> tuple[HolySiteDefinition, ...]:
        return tuple(
            definition
            for definition in self.holy_site_definitions
            if religion_name in definition.religions
        )

    def get_holy_sites_for_god(self, god_name: str) -> tuple[HolySiteDefinition, ...]:
        return tuple(
            definition
            for definition in self.holy_site_definitions
            if definition.god == god_name
        )

    def get_holy_sites_for_avatar(self, avatar_name: str) -> tuple[HolySiteDefinition, ...]:
        return tuple(
            definition
            for definition in self.holy_site_definitions
            if definition.avatar == avatar_name
        )

    def build_report(self) -> HolySiteReport:
        edges: list[HolySiteReferenceEdge] = []
        missing: set[str] = set()
        for definition in self.holy_site_definitions:
            if definition.holy_site_type is None:
                continue
            edges.append(
                HolySiteReferenceEdge(
                    source_name=definition.name,
                    referenced_names=(definition.holy_site_type,),
                )
            )
            if self.get_holy_site_type(definition.holy_site_type) is None:
                missing.add(definition.holy_site_type)
        return HolySiteReport(
            holy_site_type_links=tuple(edges),
            missing_holy_site_type_references=tuple(sorted(missing)),
        )


def parse_holy_site_document(text: str) -> HolySiteDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[HolySiteDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            HolySiteDefinition(
                name=entry.key,
                body=body,
                location=body.get_scalar("location"),
                holy_site_type=body.get_scalar("type"),
                importance=parse_int_or_none(body.get_scalar("importance")),
                religions=object_child_keys(body, "religions"),
                god=body.get_scalar("god"),
                avatar=body.get_scalar("avatar"),
                entry=entry,
            )
        )

    return HolySiteDocument(definitions=tuple(definitions), semantic_document=semantic_document)


def build_holy_site_catalog(
    holy_site_type_documents: Sequence[HolySiteTypeDocument],
    holy_site_documents: Sequence[HolySiteDocument],
) -> HolySiteCatalog:
    return HolySiteCatalog(
        holy_site_type_definitions=flatten_definitions(holy_site_type_documents),
        holy_site_definitions=flatten_definitions(holy_site_documents),
    )


def build_holy_site_report(catalog: HolySiteCatalog) -> HolySiteReport:
    return catalog.build_report()
