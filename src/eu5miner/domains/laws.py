"""Domain adapter for laws and their nested policies."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
    entry_object,
    entry_scalar_text,
    parse_bool_or_none,
    parse_int_or_none,
)
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)

LAW_RESERVED_KEYS = frozenset(
    {
        "allow",
        "custom_tags",
        "has_levels",
        "law_category",
        "law_country_group",
        "law_gov_group",
        "law_religion_group",
        "locked",
        "potential",
        "requires_vote",
        "show_tags_in_ui",
        "type",
        "unique",
    }
)


@dataclass(frozen=True)
class LawPolicyDefinition:
    name: str
    body: SemanticObject
    price: str | SemanticObject | None
    potential: SemanticObject | None
    allow: SemanticObject | None
    unique: bool | None
    custom_tags: tuple[str, ...]
    show_tags_in_ui: bool | None
    estate_preferences: tuple[str, ...]
    on_pay_price: SemanticObject | None
    on_activate: SemanticObject | None
    on_fully_activated: SemanticObject | None
    on_deactivate: SemanticObject | None
    international_organization_modifiers: tuple[SemanticObject, ...]
    country_modifiers: tuple[SemanticObject, ...]
    province_modifiers: tuple[SemanticObject, ...]
    location_modifiers: tuple[SemanticObject, ...]
    modifier: SemanticObject | None
    leader_modifier: SemanticObject | None
    non_leader_modifier: SemanticObject | None
    wants_this_policy_bias: SemanticObject | None
    wants_propose_policy: SemanticObject | None
    wants_keep_policy: SemanticObject | None
    reasons_to_join: SemanticObject | None
    diplomatic_capacity_cost: str | SemanticObject | None
    can_join_trigger: SemanticObject | None
    can_leave_trigger: SemanticObject | None
    auto_leave_trigger: SemanticObject | None
    auto_disband_trigger: SemanticObject | None
    can_declare_war: SemanticObject | None
    has_military_access: SemanticObject | None
    leader: SemanticObject | None
    leader_type: str | None
    leader_change_trigger_type: str | None
    leader_change_method: str | None
    leadership_election_resolution: str | None
    months_between_leader_changes: int | None
    has_leader_country: bool | None
    has_parliament: bool | None
    can_invite_countries: bool | None
    gives_food_access_to_members: bool | None
    has_dynastic_power: bool | None
    join_defensive_wars_always: bool | None
    join_defensive_wars_auto_call: bool | None
    join_defensive_wars_can_call: bool | None
    join_offensive_wars_always: bool | None
    join_offensive_wars_auto_call: bool | None
    join_offensive_wars_can_call: bool | None
    min_opinion: str | None
    min_trust: str | None
    antagonism_towards_leader_modifier: str | None
    antagonism_modifier_for_taking_land_from_fellow_member: str | None
    no_cb_price_modifier_for_fellow_member: str | None
    payments_implemented: tuple[str, ...]
    payments_repealed: tuple[str, ...]
    special_statuses_implemented: tuple[str, ...]
    special_statuses_repealed: tuple[str, ...]
    leader_title_key: str | None
    title_is_suffix: bool | None
    level: int | None
    years: int | None
    months: int | None
    weeks: int | None
    days: int | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class LawDefinition:
    name: str
    body: SemanticObject
    law_category: str | None
    law_type: str | None
    potential: SemanticObject | None
    allow: SemanticObject | None
    locked: SemanticObject | None
    requires_vote: bool | None
    has_levels: bool | None
    unique: bool | None
    custom_tags: tuple[str, ...]
    show_tags_in_ui: bool | None
    law_gov_groups: tuple[str, ...]
    law_religion_groups: tuple[str, ...]
    law_country_groups: tuple[str, ...]
    policies: tuple[LawPolicyDefinition, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)

    def policy_names(self) -> tuple[str, ...]:
        return tuple(policy.name for policy in self.policies)

    def get_policy(self, name: str) -> LawPolicyDefinition | None:
        for policy in self.policies:
            if policy.name == name:
                return policy
        return None


@dataclass(frozen=True)
class LawDocument:
    definitions: tuple[LawDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> LawDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


@dataclass(frozen=True)
class LawPolicyCatalog:
    law_definitions: tuple[LawDefinition, ...]

    def get_law(self, name: str) -> LawDefinition | None:
        for definition in self.law_definitions:
            if definition.name == name:
                return definition
        return None

    def get_policy(self, name: str) -> LawPolicyDefinition | None:
        for definition in self.law_definitions:
            for policy in definition.policies:
                if policy.name == name:
                    return policy
        return None

    def get_law_for_policy(self, policy_name: str) -> LawDefinition | None:
        for definition in self.law_definitions:
            if definition.get_policy(policy_name) is not None:
                return definition
        return None

    def get_policies_for_law(self, law_name: str) -> tuple[LawPolicyDefinition, ...]:
        definition = self.get_law(law_name)
        if definition is None:
            return ()
        return definition.policies

    def get_policies_for_category(self, law_category: str) -> tuple[LawPolicyDefinition, ...]:
        return tuple(
            policy
            for definition in self.law_definitions
            if definition.law_category == law_category
            for policy in definition.policies
        )


def parse_law_document(text: str) -> LawDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[LawDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            LawDefinition(
                name=entry.key,
                body=body,
                law_category=body.get_scalar("law_category"),
                law_type=body.get_scalar("type"),
                potential=body.get_object("potential"),
                allow=body.get_object("allow"),
                locked=body.get_object("locked"),
                requires_vote=parse_bool_or_none(body.get_scalar("requires_vote")),
                has_levels=parse_bool_or_none(body.get_scalar("has_levels")),
                unique=parse_bool_or_none(body.get_scalar("unique")),
                custom_tags=_collect_scalar_like_values(body.first_entry("custom_tags")),
                show_tags_in_ui=parse_bool_or_none(body.get_scalar("show_tags_in_ui")),
                law_gov_groups=_collect_scalar_like_values(body.first_entry("law_gov_group")),
                law_religion_groups=_collect_scalar_like_values(
                    body.first_entry("law_religion_group")
                ),
                law_country_groups=_collect_scalar_like_values(
                    body.first_entry("law_country_group")
                ),
                policies=_parse_policies(body),
                entry=entry,
            )
        )

    return LawDocument(definitions=tuple(definitions), semantic_document=semantic_document)


def build_law_policy_catalog(documents: Sequence[LawDocument]) -> LawPolicyCatalog:
    return LawPolicyCatalog(
        law_definitions=tuple(
            definition for document in documents for definition in document.definitions
        )
    )


def _parse_policies(body: SemanticObject) -> tuple[LawPolicyDefinition, ...]:
    policies: list[LawPolicyDefinition] = []
    for entry in body.entries:
        if entry.key in LAW_RESERVED_KEYS or not isinstance(entry.value, SemanticObject):
            continue
        policy_body = entry.value
        policies.append(
            LawPolicyDefinition(
                name=entry.key,
                body=policy_body,
                price=_parse_scalar_or_object(policy_body.first_entry("price")),
                potential=policy_body.get_object("potential"),
                allow=policy_body.get_object("allow"),
                unique=parse_bool_or_none(policy_body.get_scalar("unique")),
                custom_tags=_collect_scalar_like_values(policy_body.first_entry("custom_tags")),
                show_tags_in_ui=parse_bool_or_none(policy_body.get_scalar("show_tags_in_ui")),
                estate_preferences=_collect_scalar_like_values(
                    policy_body.first_entry("estate_preferences")
                ),
                on_pay_price=policy_body.get_object("on_pay_price"),
                on_activate=policy_body.get_object("on_activate"),
                on_fully_activated=policy_body.get_object("on_fully_activated"),
                on_deactivate=policy_body.get_object("on_deactivate"),
                international_organization_modifiers=_collect_objects(
                    policy_body, "international_organization_modifier"
                ),
                country_modifiers=_collect_objects(policy_body, "country_modifier"),
                province_modifiers=_collect_objects(policy_body, "province_modifier"),
                location_modifiers=_collect_objects(policy_body, "location_modifier"),
                modifier=policy_body.get_object("modifier"),
                leader_modifier=policy_body.get_object("leader_modifier"),
                non_leader_modifier=policy_body.get_object("non_leader_modifier"),
                wants_this_policy_bias=policy_body.get_object("wants_this_policy_bias"),
                wants_propose_policy=policy_body.get_object("wants_propose_policy"),
                wants_keep_policy=policy_body.get_object("wants_keep_policy"),
                reasons_to_join=policy_body.get_object("reasons_to_join"),
                diplomatic_capacity_cost=_parse_scalar_or_object(
                    policy_body.first_entry("diplomatic_capacity_cost")
                ),
                can_join_trigger=policy_body.get_object("can_join_trigger"),
                can_leave_trigger=policy_body.get_object("can_leave_trigger"),
                auto_leave_trigger=policy_body.get_object("auto_leave_trigger"),
                auto_disband_trigger=policy_body.get_object("auto_disband_trigger"),
                can_declare_war=policy_body.get_object("can_declare_war"),
                has_military_access=policy_body.get_object("has_military_access"),
                leader=policy_body.get_object("leader"),
                leader_type=policy_body.get_scalar("leader_type"),
                leader_change_trigger_type=policy_body.get_scalar("leader_change_trigger_type"),
                leader_change_method=policy_body.get_scalar("leader_change_method"),
                leadership_election_resolution=policy_body.get_scalar(
                    "leadership_election_resolution"
                ),
                months_between_leader_changes=parse_int_or_none(
                    policy_body.get_scalar("months_between_leader_changes")
                ),
                has_leader_country=parse_bool_or_none(policy_body.get_scalar("has_leader_country")),
                has_parliament=parse_bool_or_none(policy_body.get_scalar("has_parliament")),
                can_invite_countries=parse_bool_or_none(
                    policy_body.get_scalar("can_invite_countries")
                ),
                gives_food_access_to_members=parse_bool_or_none(
                    policy_body.get_scalar("gives_food_access_to_members")
                ),
                has_dynastic_power=parse_bool_or_none(
                    policy_body.get_scalar("has_dynastic_power")
                ),
                join_defensive_wars_always=parse_bool_or_none(
                    policy_body.get_scalar("join_defensive_wars_always")
                ),
                join_defensive_wars_auto_call=parse_bool_or_none(
                    policy_body.get_scalar("join_defensive_wars_auto_call")
                ),
                join_defensive_wars_can_call=parse_bool_or_none(
                    policy_body.get_scalar("join_defensive_wars_can_call")
                ),
                join_offensive_wars_always=parse_bool_or_none(
                    policy_body.get_scalar("join_offensive_wars_always")
                ),
                join_offensive_wars_auto_call=parse_bool_or_none(
                    policy_body.get_scalar("join_offensive_wars_auto_call")
                ),
                join_offensive_wars_can_call=parse_bool_or_none(
                    policy_body.get_scalar("join_offensive_wars_can_call")
                ),
                min_opinion=policy_body.get_scalar("min_opinion"),
                min_trust=policy_body.get_scalar("min_trust"),
                antagonism_towards_leader_modifier=policy_body.get_scalar(
                    "antagonism_towards_leader_modifier"
                ),
                antagonism_modifier_for_taking_land_from_fellow_member=policy_body.get_scalar(
                    "antagonism_modifier_for_taking_land_from_fellow_member"
                ),
                no_cb_price_modifier_for_fellow_member=policy_body.get_scalar(
                    "no_cb_price_modifier_for_fellow_member"
                ),
                payments_implemented=_collect_scalar_like_values(
                    policy_body.first_entry("payments_implemented")
                ),
                payments_repealed=_collect_scalar_like_values(
                    policy_body.first_entry("payments_repealed")
                ),
                special_statuses_implemented=_collect_scalar_like_values(
                    policy_body.first_entry("special_statuses_implemented")
                ),
                special_statuses_repealed=_collect_scalar_like_values(
                    policy_body.first_entry("special_statuses_repealed")
                ),
                leader_title_key=policy_body.get_scalar("leader_title_key"),
                title_is_suffix=parse_bool_or_none(policy_body.get_scalar("title_is_suffix")),
                level=parse_int_or_none(policy_body.get_scalar("level")),
                years=parse_int_or_none(policy_body.get_scalar("years")),
                months=parse_int_or_none(policy_body.get_scalar("months")),
                weeks=parse_int_or_none(policy_body.get_scalar("weeks")),
                days=parse_int_or_none(policy_body.get_scalar("days")),
                entry=entry,
            )
        )
    return tuple(policies)


def _collect_objects(body: SemanticObject, key: str) -> tuple[SemanticObject, ...]:
    return tuple(
        entry.value
        for entry in body.find_entries(key)
        if isinstance(entry.value, SemanticObject)
    )


def _collect_scalar_like_values(entry: SemanticEntry | None) -> tuple[str, ...]:
    if entry is None:
        return ()
    if isinstance(entry.value, SemanticScalar):
        return tuple(part for part in entry.value.text.split() if part)
    if isinstance(entry.value, SemanticObject):
        values: list[str] = []
        for child in entry.value.entries:
            if child.operator is None and child.value is None:
                values.append(child.key)
                continue
            if isinstance(child.value, SemanticScalar):
                values.append(child.value.text)
        return tuple(values)
    if entry.operator is None and entry.value is None:
        return (entry.key,)
    return ()


def _parse_scalar_or_object(entry: SemanticEntry | None) -> str | SemanticObject | None:
    scalar = entry_scalar_text(entry)
    if scalar is not None:
        return scalar
    return entry_object(entry)
