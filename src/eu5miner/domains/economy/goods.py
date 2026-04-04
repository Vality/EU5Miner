"""Domain adapter for goods definitions."""

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
class GoodsAmount:
    """One scalar amount entry inside a goods sub-block."""

    name: str
    amount: str
    entry: SemanticEntry


@dataclass(frozen=True)
class GoodsDefinition:
    """One goods definition."""

    name: str
    body: SemanticObject
    method: str | None
    category: str | None
    color: str | None
    is_slaves: bool | None
    block_rgo_upgrade: bool | None
    inflation: bool | None
    base_production: str | None
    food: str | None
    transport_cost: str | None
    default_market_price: str | None
    ai_rgo_size_importance: str | None
    ai_rgo_expansion_priority: str | None
    origin_in_old_world: bool | None
    origin_in_new_world: bool | None
    demand_add: tuple[GoodsAmount, ...]
    demand_multiply: tuple[GoodsAmount, ...]
    wealth_impact_threshold: tuple[GoodsAmount, ...]
    custom_tags: tuple[str, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class GoodsDocument:
    """Parsed goods file."""

    definitions: tuple[GoodsDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> GoodsDefinition | None:
        return get_by_name(self.definitions, name)


def parse_goods_document(text: str) -> GoodsDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[GoodsDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            GoodsDefinition(
                name=entry.key,
                body=body,
                method=body.get_scalar("method"),
                category=body.get_scalar("category"),
                color=body.get_scalar("color"),
                is_slaves=parse_bool_or_none(body.get_scalar("is_slaves")),
                block_rgo_upgrade=parse_bool_or_none(body.get_scalar("block_rgo_upgrade")),
                inflation=parse_bool_or_none(body.get_scalar("inflation")),
                base_production=body.get_scalar("base_production"),
                food=body.get_scalar("food"),
                transport_cost=body.get_scalar("transport_cost"),
                default_market_price=body.get_scalar("default_market_price"),
                ai_rgo_size_importance=body.get_scalar("ai_rgo_size_importance"),
                ai_rgo_expansion_priority=body.get_scalar("ai_rgo_expansion_priority"),
                origin_in_old_world=parse_bool_or_none(body.get_scalar("origin_in_old_world")),
                origin_in_new_world=parse_bool_or_none(body.get_scalar("origin_in_new_world")),
                demand_add=_parse_amount_block(body.get_object("demand_add")),
                demand_multiply=_parse_amount_block(body.get_object("demand_multiply")),
                wealth_impact_threshold=_parse_amount_block(
                    body.get_object("wealth_impact_threshold")
                ),
                custom_tags=_collect_scalar_like_list(body.get_object("custom_tags")),
                entry=entry,
            )
        )

    return GoodsDocument(definitions=tuple(definitions), semantic_document=semantic_document)


def _parse_amount_block(block: SemanticObject | None) -> tuple[GoodsAmount, ...]:
    if block is None:
        return ()

    amounts: list[GoodsAmount] = []
    for entry in block.entries:
        if isinstance(entry.value, SemanticScalar):
            amounts.append(GoodsAmount(name=entry.key, amount=entry.value.text, entry=entry))
    return tuple(amounts)


def _collect_scalar_like_list(block: SemanticObject | None) -> tuple[str, ...]:
    if block is None:
        return ()

    values: list[str] = []
    for entry in block.entries:
        if entry.operator is None and entry.value is None:
            values.append(entry.key)
        elif isinstance(entry.value, SemanticScalar):
            values.append(entry.value.text)
    return tuple(values)
