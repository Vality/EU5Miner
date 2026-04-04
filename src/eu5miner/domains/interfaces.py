"""Shared interfaces and lookup helpers for domain definitions and documents."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Protocol, TypeVar, runtime_checkable

from eu5miner.formats.semantic import SemanticObject


@runtime_checkable
class NamedDefinitionLike(Protocol):
    @property
    def name(self) -> str: ...


@runtime_checkable
class TaggedDefinitionLike(Protocol):
    @property
    def tag(self) -> str: ...


@runtime_checkable
class BodyBackedDefinitionLike(Protocol):
    @property
    def body(self) -> SemanticObject: ...


NamedDefinitionT = TypeVar("NamedDefinitionT", bound=NamedDefinitionLike)
TaggedDefinitionT = TypeVar("TaggedDefinitionT", bound=TaggedDefinitionLike)
NamedDefinitionDocT = TypeVar(
    "NamedDefinitionDocT",
    bound=NamedDefinitionLike,
    covariant=True,
)
TaggedDefinitionDocT = TypeVar(
    "TaggedDefinitionDocT",
    bound=TaggedDefinitionLike,
    covariant=True,
)


@runtime_checkable
class NamedDefinitionDocumentLike(Protocol[NamedDefinitionDocT]):
    @property
    def definitions(self) -> tuple[NamedDefinitionDocT, ...]: ...

    def names(self) -> tuple[str, ...]: ...

    def get_definition(self, name: str) -> NamedDefinitionDocT | None: ...


@runtime_checkable
class TaggedDefinitionDocumentLike(Protocol[TaggedDefinitionDocT]):
    @property
    def definitions(self) -> tuple[TaggedDefinitionDocT, ...]: ...

    def get_definition(self, tag: str) -> TaggedDefinitionDocT | None: ...


def names_from_named(definitions: Sequence[NamedDefinitionLike]) -> tuple[str, ...]:
    return tuple(definition.name for definition in definitions)


def get_by_name[NamedDefinitionT: NamedDefinitionLike](
    definitions: Sequence[NamedDefinitionT],
    name: str,
) -> NamedDefinitionT | None:
    for definition in definitions:
        if definition.name == name:
            return definition
    return None


def tags_from_tagged(definitions: Sequence[TaggedDefinitionLike]) -> tuple[str, ...]:
    return tuple(definition.tag for definition in definitions)


def get_by_tag[TaggedDefinitionT: TaggedDefinitionLike](
    definitions: Sequence[TaggedDefinitionT],
    tag: str,
) -> TaggedDefinitionT | None:
    for definition in definitions:
        if definition.tag == tag:
            return definition
    return None


def flatten_definitions[NamedDefinitionDocT: NamedDefinitionLike](
    documents: Iterable[NamedDefinitionDocumentLike[NamedDefinitionDocT]],
) -> tuple[NamedDefinitionDocT, ...]:
    return tuple(definition for document in documents for definition in document.definitions)


def get_scalar_from_body(definition: BodyBackedDefinitionLike, key: str) -> str | None:
    return definition.body.get_scalar(key)
