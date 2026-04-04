"""Domain adapter for subject type definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
    entry_object,
    entry_scalar_text,
    parse_bool_or_none,
    parse_float_or_none,
    parse_int_or_none,
)
from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class SubjectTypeDefinition:
    """One subject type definition."""

    name: str
    body: SemanticObject
    color: str | None
    subject_kind: str | None
    government: str | None
    level: int | None
    minimum_opinion_for_offer: int | None
    annullment_favours_required: int | None
    annexation_min_years_before: int | None
    annexation_min_opinion: int | None
    annexation_stall_opinion: int | None
    subject_pays: str | SemanticObject | None
    great_power_score_transfer: float | None
    diplomatic_capacity_cost_scale: float | None
    strength_vs_overlord: float | None
    merchants_to_overlord_fraction: float | None
    war_score_cost: str | SemanticObject | None
    base_antagonism: str | SemanticObject | None
    monthly_favor_gain: str | SemanticObject | None
    institution_spread_to_overlord: str | SemanticObject | None
    institution_spread_to_subject: str | SemanticObject | None
    visible_through_diplomacy: SemanticObject | None
    enabled_through_diplomacy: SemanticObject | None
    visible_through_treaty: SemanticObject | None
    enabled_through_treaty: SemanticObject | None
    creation_visible: SemanticObject | None
    subject_creation_enabled: SemanticObject | None
    release_country_enabled: SemanticObject | None
    can_attack: SemanticObject | None
    can_rival: SemanticObject | None
    can_marry: SemanticObject | None
    join_offensive_wars_always: SemanticObject | None
    join_offensive_wars_auto_call: SemanticObject | None
    join_offensive_wars_can_call: SemanticObject | None
    join_defensive_wars_always: SemanticObject | None
    join_defensive_wars_auto_call: SemanticObject | None
    join_defensive_wars_can_call: SemanticObject | None
    allow_declaring_wars: SemanticObject | None
    overlord_modifier: SemanticObject | None
    subject_modifier: SemanticObject | None
    on_enable: SemanticObject | None
    on_disable: SemanticObject | None
    on_monthly: SemanticObject | None
    diplo_chance_accept_subject: SemanticObject | None
    diplo_chance_accept_overlord: SemanticObject | None
    ai_wants_to_be_overlord: SemanticObject | None
    ai_wants_to_be_subject: SemanticObject | None
    can_be_annexed: bool | None
    has_overlords_ruler: bool | None
    has_overlords_religion: bool | None
    has_limited_diplomacy: bool | None
    can_change_rank: bool | None
    can_change_heir_selection: bool | None
    subject_can_cancel: bool | None
    overlord_can_cancel: bool | None
    will_join_independence_wars: bool | None
    fleet_basing_rights: bool | None
    food_access: bool | None
    use_overlord_laws: bool | None
    annulled_by_peace_treaty: bool | None
    use_overlord_map_color: bool | None
    use_overlord_map_name: bool | None
    only_overlord_culture: bool | None
    only_overlord_or_kindred_culture: bool | None
    only_overlord_court_language: bool | None
    can_overlord_recruit_regiments: bool | None
    can_overlord_build_ships: bool | None
    can_overlord_build_roads: bool | None
    can_overlord_build_buildings: bool | None
    can_overlord_build_rgos: bool | None
    overlord_share_exploration: bool | None
    overlord_protects_external: bool | None
    overlord_protects_other_subjects: bool | None
    can_be_force_broken_in_peace_treaty: bool | None
    overlord_can_enforce_peace_on_subject: bool | None
    allow_subjects: bool | None
    overlord_inherit_if_no_heir: bool | None
    is_colonial_subject: bool | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class SubjectTypeDocument:
    """Parsed subject type file."""

    definitions: tuple[SubjectTypeDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> SubjectTypeDefinition | None:
        return get_by_name(self.definitions, name)


def parse_subject_type_document(text: str) -> SubjectTypeDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[SubjectTypeDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            SubjectTypeDefinition(
                name=entry.key,
                body=body,
                color=body.get_scalar("color"),
                subject_kind=body.get_scalar("type"),
                government=body.get_scalar("government"),
                level=parse_int_or_none(body.get_scalar("level")),
                minimum_opinion_for_offer=parse_int_or_none(
                    body.get_scalar("minimum_opinion_for_offer")
                ),
                annullment_favours_required=parse_int_or_none(
                    body.get_scalar("annullment_favours_required")
                ),
                annexation_min_years_before=parse_int_or_none(
                    body.get_scalar("annexation_min_years_before")
                ),
                annexation_min_opinion=parse_int_or_none(body.get_scalar("annexation_min_opinion")),
                annexation_stall_opinion=parse_int_or_none(
                    body.get_scalar("annexation_stall_opinion")
                ),
                subject_pays=_parse_scalar_or_object(body.first_entry("subject_pays")),
                great_power_score_transfer=parse_float_or_none(
                    body.get_scalar("great_power_score_transfer")
                ),
                diplomatic_capacity_cost_scale=parse_float_or_none(
                    body.get_scalar("diplomatic_capacity_cost_scale")
                ),
                strength_vs_overlord=parse_float_or_none(body.get_scalar("strength_vs_overlord")),
                merchants_to_overlord_fraction=parse_float_or_none(
                    body.get_scalar("merchants_to_overlord_fraction")
                ),
                war_score_cost=_parse_scalar_or_object(body.first_entry("war_score_cost")),
                base_antagonism=_parse_scalar_or_object(body.first_entry("base_antagonism")),
                monthly_favor_gain=_parse_scalar_or_object(body.first_entry("monthly_favor_gain")),
                institution_spread_to_overlord=_parse_scalar_or_object(
                    body.first_entry("institution_spread_to_overlord")
                ),
                institution_spread_to_subject=_parse_scalar_or_object(
                    body.first_entry("institution_spread_to_subject")
                ),
                visible_through_diplomacy=body.get_object("visible_through_diplomacy"),
                enabled_through_diplomacy=body.get_object("enabled_through_diplomacy"),
                visible_through_treaty=body.get_object("visible_through_treaty"),
                enabled_through_treaty=body.get_object("enabled_through_treaty"),
                creation_visible=body.get_object("creation_visible"),
                subject_creation_enabled=body.get_object("subject_creation_enabled"),
                release_country_enabled=body.get_object("release_country_enabled"),
                can_attack=body.get_object("can_attack"),
                can_rival=body.get_object("can_rival"),
                can_marry=body.get_object("can_marry"),
                join_offensive_wars_always=body.get_object("join_offensive_wars_always"),
                join_offensive_wars_auto_call=body.get_object("join_offensive_wars_auto_call"),
                join_offensive_wars_can_call=body.get_object("join_offensive_wars_can_call"),
                join_defensive_wars_always=body.get_object("join_defensive_wars_always"),
                join_defensive_wars_auto_call=body.get_object("join_defensive_wars_auto_call"),
                join_defensive_wars_can_call=body.get_object("join_defensive_wars_can_call"),
                allow_declaring_wars=body.get_object("allow_declaring_wars"),
                overlord_modifier=body.get_object("overlord_modifier"),
                subject_modifier=body.get_object("subject_modifier"),
                on_enable=body.get_object("on_enable"),
                on_disable=body.get_object("on_disable"),
                on_monthly=body.get_object("on_monthly"),
                diplo_chance_accept_subject=body.get_object("diplo_chance_accept_subject"),
                diplo_chance_accept_overlord=body.get_object("diplo_chance_accept_overlord"),
                ai_wants_to_be_overlord=body.get_object("ai_wants_to_be_overlord"),
                ai_wants_to_be_subject=body.get_object("ai_wants_to_be_subject"),
                can_be_annexed=parse_bool_or_none(body.get_scalar("can_be_annexed")),
                has_overlords_ruler=parse_bool_or_none(body.get_scalar("has_overlords_ruler")),
                has_overlords_religion=parse_bool_or_none(
                    body.get_scalar("has_overlords_religion")
                ),
                has_limited_diplomacy=parse_bool_or_none(body.get_scalar("has_limited_diplomacy")),
                can_change_rank=parse_bool_or_none(body.get_scalar("can_change_rank")),
                can_change_heir_selection=parse_bool_or_none(
                    body.get_scalar("can_change_heir_selection")
                ),
                subject_can_cancel=parse_bool_or_none(body.get_scalar("subject_can_cancel")),
                overlord_can_cancel=parse_bool_or_none(body.get_scalar("overlord_can_cancel")),
                will_join_independence_wars=parse_bool_or_none(
                    body.get_scalar("will_join_independence_wars")
                ),
                fleet_basing_rights=parse_bool_or_none(body.get_scalar("fleet_basing_rights")),
                food_access=parse_bool_or_none(body.get_scalar("food_access")),
                use_overlord_laws=parse_bool_or_none(body.get_scalar("use_overlord_laws")),
                annulled_by_peace_treaty=parse_bool_or_none(
                    body.get_scalar("annulled_by_peace_treaty")
                ),
                use_overlord_map_color=parse_bool_or_none(
                    body.get_scalar("use_overlord_map_color")
                ),
                use_overlord_map_name=parse_bool_or_none(body.get_scalar("use_overlord_map_name")),
                only_overlord_culture=parse_bool_or_none(body.get_scalar("only_overlord_culture")),
                only_overlord_or_kindred_culture=parse_bool_or_none(
                    body.get_scalar("only_overlord_or_kindred_culture")
                ),
                only_overlord_court_language=parse_bool_or_none(
                    body.get_scalar("only_overlord_court_language")
                ),
                can_overlord_recruit_regiments=parse_bool_or_none(
                    body.get_scalar("can_overlord_recruit_regiments")
                ),
                can_overlord_build_ships=parse_bool_or_none(
                    body.get_scalar("can_overlord_build_ships")
                ),
                can_overlord_build_roads=parse_bool_or_none(
                    body.get_scalar("can_overlord_build_roads")
                ),
                can_overlord_build_buildings=parse_bool_or_none(
                    body.get_scalar("can_overlord_build_buildings")
                ),
                can_overlord_build_rgos=parse_bool_or_none(
                    body.get_scalar("can_overlord_build_rgos")
                ),
                overlord_share_exploration=parse_bool_or_none(
                    body.get_scalar("overlord_share_exploration")
                ),
                overlord_protects_external=parse_bool_or_none(
                    body.get_scalar("overlord_protects_external")
                ),
                overlord_protects_other_subjects=parse_bool_or_none(
                    body.get_scalar("overlord_protects_other_subjects")
                ),
                can_be_force_broken_in_peace_treaty=parse_bool_or_none(
                    body.get_scalar("can_be_force_broken_in_peace_treaty")
                ),
                overlord_can_enforce_peace_on_subject=parse_bool_or_none(
                    body.get_scalar("overlord_can_enforce_peace_on_subject")
                ),
                allow_subjects=parse_bool_or_none(body.get_scalar("allow_subjects")),
                overlord_inherit_if_no_heir=parse_bool_or_none(
                    body.get_scalar("overlord_inherit_if_no_heir")
                ),
                is_colonial_subject=parse_bool_or_none(body.get_scalar("is_colonial_subject")),
                entry=entry,
            )
        )

    return SubjectTypeDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_scalar_or_object(
    entry: SemanticEntry | None,
) -> str | SemanticObject | None:
    scalar = entry_scalar_text(entry)
    if scalar is not None:
        return scalar
    return entry_object(entry)
