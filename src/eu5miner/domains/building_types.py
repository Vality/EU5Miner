"""Domain adapter for building type definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._macros import collect_parameters_from_object
from eu5miner.domains._parse_helpers import parse_bool_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)

_LOCATION_RANK_KEYS = ("rural_settlement", "town", "city")


@dataclass(frozen=True)
class BuildingTypeDefinition:
    """One building type definition."""

    name: str
    body: SemanticObject
    category: str | None
    pop_type: str | None
    build_time: str | None
    employment_size: str | None
    output: str | None
    is_foreign: bool | None
    in_empty: str | None
    stronger_power_projection: bool | None
    need_good_relation: bool | None
    conversion_religion: str | None
    obsolete: str | None
    price: str | None
    destroy_price: str | None
    estate: str | None
    max_levels: str | None
    construction_demand: str | None
    increase_per_level_cost: str | None
    forbidden_for_estates: bool | None
    expensive: bool | None
    is_indestructible: bool | None
    always_add_demands: bool | None
    ai_ignore_available_worker_flag: bool | None
    important_for_ai: bool | None
    important_for_ui: bool | None
    allow: SemanticObject | None
    location_potential: SemanticObject | None
    country_potential: SemanticObject | None
    can_destroy: SemanticObject | None
    remove_if: SemanticObject | None
    capital_modifier: SemanticObject | None
    capital_country_modifier: SemanticObject | None
    modifier: SemanticObject | None
    raw_modifier: SemanticObject | None
    market_center_modifier: SemanticObject | None
    on_built: SemanticObject | None
    on_destroyed: SemanticObject | None
    unique_production_methods: SemanticObject | None
    possible_production_methods: tuple[tuple[str, ...], ...]
    custom_tags: tuple[str, ...]
    graphical_tags: tuple[str, ...]
    location_ranks: tuple[str, ...]
    parameters: tuple[str, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class BuildingTypeDocument:
    """Parsed building type file."""

    definitions: tuple[BuildingTypeDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> BuildingTypeDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_building_type_document(text: str) -> BuildingTypeDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[BuildingTypeDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            BuildingTypeDefinition(
                name=entry.key,
                body=body,
                category=body.get_scalar("category"),
                pop_type=body.get_scalar("pop_type"),
                build_time=body.get_scalar("build_time"),
                employment_size=body.get_scalar("employment_size"),
                output=body.get_scalar("output"),
                is_foreign=parse_bool_or_none(body.get_scalar("is_foreign")),
                in_empty=body.get_scalar("in_empty"),
                stronger_power_projection=parse_bool_or_none(
                    body.get_scalar("stronger_power_projection")
                ),
                need_good_relation=parse_bool_or_none(
                    body.get_scalar("need_good_relation")
                ),
                conversion_religion=body.get_scalar("conversion_religion"),
                obsolete=body.get_scalar("obsolete"),
                price=body.get_scalar("price"),
                destroy_price=body.get_scalar("destroy_price"),
                estate=body.get_scalar("estate"),
                max_levels=body.get_scalar("max_levels"),
                construction_demand=body.get_scalar("construction_demand"),
                increase_per_level_cost=body.get_scalar("increase_per_level_cost"),
                forbidden_for_estates=parse_bool_or_none(
                    body.get_scalar("forbidden_for_estates")
                ),
                expensive=parse_bool_or_none(body.get_scalar("expensive")),
                is_indestructible=parse_bool_or_none(
                    body.get_scalar("is_indestructible")
                ),
                always_add_demands=parse_bool_or_none(
                    body.get_scalar("always_add_demands")
                ),
                ai_ignore_available_worker_flag=parse_bool_or_none(
                    body.get_scalar("AI_ignore_available_worker_flag")
                ),
                important_for_ai=parse_bool_or_none(body.get_scalar("important_for_AI")),
                important_for_ui=parse_bool_or_none(body.get_scalar("important_for_UI")),
                allow=body.get_object("allow"),
                location_potential=body.get_object("location_potential"),
                country_potential=body.get_object("country_potential"),
                can_destroy=body.get_object("can_destroy"),
                remove_if=body.get_object("remove_if"),
                capital_modifier=body.get_object("capital_modifier"),
                capital_country_modifier=body.get_object("capital_country_modifier"),
                modifier=body.get_object("modifier"),
                raw_modifier=body.get_object("raw_modifier"),
                market_center_modifier=body.get_object("market_center_modifier"),
                on_built=body.get_object("on_built"),
                on_destroyed=body.get_object("on_destroyed"),
                unique_production_methods=body.get_object("unique_production_methods"),
                possible_production_methods=_parse_possible_production_methods(body),
                custom_tags=_collect_scalar_like_list(body.get_object("custom_tags")),
                graphical_tags=_collect_scalar_like_list(body.get_object("graphical_tags")),
                location_ranks=tuple(
                    key for key in _LOCATION_RANK_KEYS if body.get_scalar(key) == "yes"
                ),
                parameters=tuple(sorted(collect_parameters_from_object(body))),
                entry=entry,
            )
        )

    return BuildingTypeDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
def _parse_possible_production_methods(
    body: SemanticObject,
) -> tuple[tuple[str, ...], ...]:
    method_lists: list[tuple[str, ...]] = []
    for entry in body.find_entries("possible_production_methods"):
        if not isinstance(entry.value, SemanticObject):
            continue
        method_lists.append(_collect_scalar_like_list(entry.value))
    return tuple(method_lists)


def _collect_scalar_like_list(block: SemanticObject | None) -> tuple[str, ...]:
    if block is None:
        return ()

    values: list[str] = []
    for entry in block.entries:
        if entry.operator is None and entry.value is None:
            values.append(entry.key)
            continue
        if isinstance(entry.value, SemanticScalar):
            values.append(entry.value.text)
    return tuple(values)
