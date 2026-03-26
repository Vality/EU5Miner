"""Shared interfaces and lookup helpers for domain definitions and documents."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TypeVar, runtime_checkable


@runtime_checkable
class NamedDefinitionLike(Protocol):
    @property
    def name(self) -> str: ...


@runtime_checkable
class TaggedDefinitionLike(Protocol):
    @property
    def tag(self) -> str: ...


NamedDefinitionT = TypeVar("NamedDefinitionT", bound=NamedDefinitionLike)
TaggedDefinitionT = TypeVar("TaggedDefinitionT", bound=TaggedDefinitionLike)
NamedDefinitionDocT = TypeVar("NamedDefinitionDocT", bound=NamedDefinitionLike)
TaggedDefinitionDocT = TypeVar("TaggedDefinitionDocT", bound=TaggedDefinitionLike)


@runtime_checkable
class NamedDefinitionDocumentLike(Protocol[NamedDefinitionDocT]):
    definitions: tuple[NamedDefinitionDocT, ...]

    def names(self) -> tuple[str, ...]: ...

    def get_definition(self, name: str) -> NamedDefinitionDocT | None: ...


@runtime_checkable
class TaggedDefinitionDocumentLike(Protocol[TaggedDefinitionDocT]):
    definitions: tuple[TaggedDefinitionDocT, ...]

    def get_definition(self, tag: str) -> TaggedDefinitionDocT | None: ...


def names_from_named(definitions: Sequence[NamedDefinitionLike]) -> tuple[str, ...]:
    return tuple(definition.name for definition in definitions)


def get_by_name(
    definitions: Sequence[NamedDefinitionT],
    name: str,
) -> NamedDefinitionT | None:
    for definition in definitions:
        if definition.name == name:
            return definition
    return None


def tags_from_tagged(definitions: Sequence[TaggedDefinitionLike]) -> tuple[str, ...]:
    return tuple(definition.tag for definition in definitions)


def get_by_tag(
    definitions: Sequence[TaggedDefinitionT],
    tag: str,
) -> TaggedDefinitionT | None:
    for definition in definitions:
        if definition.tag == tag:
            return definition
    return None
