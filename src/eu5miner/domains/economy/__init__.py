"""Higher-level helpers over economy and market-adjacent domain adapters."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from eu5miner.domains.attribute_columns import (
    AttributeColumnDefinition,
    AttributeColumnDocument,
    AttributeColumnGroupDefinition,
)
from eu5miner.domains.diplomacy.generic_actions import (
    GenericActionDefinition,
    GenericActionDocument,
)
from eu5miner.domains.economy.goods import GoodsDefinition, GoodsDocument
from eu5miner.domains.economy.prices import PriceDefinition, PriceDocument
from eu5miner.domains.interfaces import flatten_definitions, get_by_name


@dataclass(frozen=True)
class MarketReferenceEdge:
    source_name: str
    referenced_names: tuple[str, ...]


@dataclass(frozen=True)
class MarketReport:
    action_target_links: tuple[MarketReferenceEdge, ...]
    available_attribute_groups: tuple[str, ...]
    priced_goods: tuple[str, ...]


@dataclass(frozen=True)
class MarketCatalog:
    goods_definitions: tuple[GoodsDefinition, ...] = ()
    price_definitions: tuple[PriceDefinition, ...] = ()
    generic_action_definitions: tuple[GenericActionDefinition, ...] = ()
    attribute_group_definitions: tuple[AttributeColumnGroupDefinition, ...] = ()

    def get_good(self, name: str) -> GoodsDefinition | None:
        return get_by_name(self.goods_definitions, name)

    def get_price(self, name: str) -> PriceDefinition | None:
        return get_by_name(self.price_definitions, name)

    def get_generic_action(self, name: str) -> GenericActionDefinition | None:
        return get_by_name(self.generic_action_definitions, name)

    def get_attribute_group(self, name: str) -> AttributeColumnGroupDefinition | None:
        return get_by_name(self.attribute_group_definitions, name)

    def get_actions_for_target(self, target_name: str) -> tuple[GenericActionDefinition, ...]:
        return tuple(
            definition
            for definition in self.generic_action_definitions
            if target_name in _collect_select_trigger_targets(definition)
        )

    def get_market_actions(self) -> tuple[GenericActionDefinition, ...]:
        return self.get_actions_for_target("market")

    def get_goods_with_default_market_price(self) -> tuple[GoodsDefinition, ...]:
        return tuple(
            definition
            for definition in self.goods_definitions
            if definition.default_market_price is not None
        )

    def get_columns_for_group(self, group_name: str) -> tuple[AttributeColumnDefinition, ...]:
        group = self.get_attribute_group(group_name)
        if group is None:
            return ()
        return group.columns

    def build_report(self) -> MarketReport:
        action_target_links = tuple(
            MarketReferenceEdge(
                source_name=definition.name,
                referenced_names=targets,
            )
            for definition in self.generic_action_definitions
            if (targets := _collect_select_trigger_targets(definition))
        )
        return MarketReport(
            action_target_links=action_target_links,
            available_attribute_groups=tuple(
                sorted(definition.name for definition in self.attribute_group_definitions)
            ),
            priced_goods=tuple(
                sorted(definition.name for definition in self.get_goods_with_default_market_price())
            ),
        )


def build_market_catalog(
    goods_documents: Sequence[GoodsDocument],
    price_documents: Sequence[PriceDocument] = (),
    generic_action_documents: Sequence[GenericActionDocument] = (),
    attribute_column_documents: Sequence[AttributeColumnDocument] = (),
) -> MarketCatalog:
    return MarketCatalog(
        goods_definitions=flatten_definitions(goods_documents),
        price_definitions=flatten_definitions(price_documents),
        generic_action_definitions=flatten_definitions(generic_action_documents),
        attribute_group_definitions=_flatten_attribute_groups(attribute_column_documents),
    )


def build_market_report(catalog: MarketCatalog) -> MarketReport:
    return catalog.build_report()


def _flatten_attribute_groups(
    documents: Sequence[AttributeColumnDocument],
) -> tuple[AttributeColumnGroupDefinition, ...]:
    return tuple(definition for document in documents for definition in document.groups)


def _collect_select_trigger_targets(
    definition: GenericActionDefinition,
) -> tuple[str, ...]:
    targets: list[str] = []
    seen: set[str] = set()
    for select_trigger in definition.select_triggers:
        target = select_trigger.looking_for_a
        if target is None or target in seen:
            continue
        seen.add(target)
        targets.append(target)
    return tuple(targets)


__all__ = [
    "MarketCatalog",
    "MarketReferenceEdge",
    "MarketReport",
    "build_market_catalog",
    "build_market_report",
]
