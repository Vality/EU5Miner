"""Domain adapter for goods demand definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)


@dataclass(frozen=True)
class GoodsDemandAmount:
    """One scalar demand amount entry."""

    name: str
    amount: str
    entry: SemanticEntry


@dataclass(frozen=True)
class ScriptedGoodsDemand:
    """One object-valued demand entry such as a scripted pop demand."""

    name: str
    body: SemanticObject
    entry: SemanticEntry


@dataclass(frozen=True)
class GoodsDemandDefinition:
    """One goods demand definition."""

    name: str
    body: SemanticObject
    category: str | None
    hidden: bool | None
    scalar_demands: tuple[GoodsDemandAmount, ...]
    scripted_demands: tuple[ScriptedGoodsDemand, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class GoodsDemandDocument:
    """Parsed goods demand file."""

    definitions: tuple[GoodsDemandDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> GoodsDemandDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_goods_demand_document(text: str) -> GoodsDemandDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[GoodsDemandDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        scalar_demands: list[GoodsDemandAmount] = []
        scripted_demands: list[ScriptedGoodsDemand] = []
        for child in body.entries:
            if child.key in {"category", "hidden"}:
                continue
            if isinstance(child.value, SemanticScalar):
                scalar_demands.append(
                    GoodsDemandAmount(name=child.key, amount=child.value.text, entry=child)
                )
            elif isinstance(child.value, SemanticObject):
                scripted_demands.append(
                    ScriptedGoodsDemand(name=child.key, body=child.value, entry=child)
                )

        definitions.append(
            GoodsDemandDefinition(
                name=entry.key,
                body=body,
                category=body.get_scalar("category"),
                hidden=_parse_bool_or_none(body.get_scalar("hidden")),
                scalar_demands=tuple(scalar_demands),
                scripted_demands=tuple(scripted_demands),
                entry=entry,
            )
        )

    return GoodsDemandDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_bool_or_none(value: str | None) -> bool | None:
    if value == "yes":
        return True
    if value == "no":
        return False
    return None
