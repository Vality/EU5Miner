"""Domain adapter for scripted relation definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
    body_value_text,
    parse_bool_or_none,
    parse_int_or_none,
)
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class ScriptedRelationDefinition:
    """One scripted relation definition."""

    name: str
    body: SemanticObject
    relation_kind: str | None
    relation_type: str | None
    uses_diplo_capacity: str | None
    relation_type_for_ai: str | None
    diplomatic_capacity_cost: str | None
    diplomatic_cost: str | None
    war_declaration_cost: str | None
    buy_price: str | None
    monthly_ongoing_price_first_country: str | None
    monthly_ongoing_price_second_country: str | None
    trade_to_first: str | None
    trade_to_second: str | None
    gold_to_first: str | None
    gold_to_second: str | None
    favors_to_first: str | None
    favors_to_second: str | None
    institution_spread_to_first: str | None
    institution_spread_to_second: str | None
    annullment_favours_required: int | None
    sound: str | None
    mutual_color: str | None
    giving_color: str | None
    receiving_color: str | None
    texture_file: str | None
    concept: str | None
    block_when_at_war: bool | None
    break_on_war: bool | None
    break_on_becoming_subject: bool | None
    break_on_not_spying: bool | None
    annulled_by_peace_treaty: bool | None
    disallow_war: bool | None
    embargo: bool | None
    military_access: bool | None
    fleet_basing_rights: bool | None
    food_access: bool | None
    is_exempt_from_sound_toll: bool | None
    is_exempt_from_isolation: bool | None
    block_building: bool | None
    skip_diplomat_for_cancel: bool | None
    lifts_fog_of_war: bool | None
    lifts_trade_protection: bool | None
    show_break_alert: bool | None
    is_ongoing: bool | None
    can_share_maps: bool | None
    category: SemanticObject | None
    visible: SemanticObject | None
    offer_visible: SemanticObject | None
    request_visible: SemanticObject | None
    cancel_visible: SemanticObject | None
    break_visible: SemanticObject | None
    offer_enabled: SemanticObject | None
    request_enabled: SemanticObject | None
    cancel_enabled: SemanticObject | None
    break_enabled: SemanticObject | None
    will_expire_trigger: SemanticObject | None
    should_ai_offer_trigger: SemanticObject | None
    wants_to_give: SemanticObject | None
    wants_to_receive: SemanticObject | None
    wants_to_give_diplo_chance: SemanticObject | None
    wants_to_receive_diplo_chance: SemanticObject | None
    wants_to_keep: SemanticObject | None
    wants_to_keep_diplo_chance: SemanticObject | None
    giving_modifier_scale: SemanticObject | None
    receiving_modifier_scale: SemanticObject | None
    mutual_modifier_scale: SemanticObject | None
    offer_effect: SemanticObject | None
    request_effect: SemanticObject | None
    cancel_effect: SemanticObject | None
    break_effect: SemanticObject | None
    offer_declined_effect: SemanticObject | None
    request_declined_effect: SemanticObject | None
    expire_effect: SemanticObject | None
    progress: SemanticObject | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class ScriptedRelationDocument:
    """Parsed scripted relation file."""

    definitions: tuple[ScriptedRelationDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> ScriptedRelationDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_scripted_relation_document(text: str) -> ScriptedRelationDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[ScriptedRelationDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            ScriptedRelationDefinition(
                name=entry.key,
                body=body,
                relation_kind=body.get_scalar("type"),
                relation_type=body.get_scalar("relation_type"),
                uses_diplo_capacity=body.get_scalar("uses_diplo_capacity"),
                relation_type_for_ai=body.get_scalar("relation_type_for_ai"),
                diplomatic_capacity_cost=body.get_scalar("diplomatic_capacity_cost"),
                diplomatic_cost=body.get_scalar("diplomatic_cost"),
                war_declaration_cost=body.get_scalar("war_declaration_cost"),
                buy_price=body.get_scalar("buy_price"),
                monthly_ongoing_price_first_country=body.get_scalar(
                    "monthly_ongoing_price_first_country"
                ),
                monthly_ongoing_price_second_country=body.get_scalar(
                    "monthly_ongoing_price_second_country"
                ),
                trade_to_first=body_value_text(body, "trade_to_first"),
                trade_to_second=body_value_text(body, "trade_to_second"),
                gold_to_first=body_value_text(body, "gold_to_first"),
                gold_to_second=body_value_text(body, "gold_to_second"),
                favors_to_first=body_value_text(body, "favors_to_first"),
                favors_to_second=body_value_text(body, "favors_to_second"),
                institution_spread_to_first=body_value_text(
                    body, "institution_spread_to_first"
                ),
                institution_spread_to_second=body_value_text(
                    body, "institution_spread_to_second"
                ),
                annullment_favours_required=parse_int_or_none(
                    body.get_scalar("annullment_favours_required")
                ),
                sound=body.get_scalar("sound"),
                mutual_color=body_value_text(body, "mutual_color"),
                giving_color=body_value_text(body, "giving_color"),
                receiving_color=body_value_text(body, "receiving_color"),
                texture_file=body.get_scalar("texture_file"),
                concept=body.get_scalar("concept"),
                block_when_at_war=parse_bool_or_none(body.get_scalar("block_when_at_war")),
                break_on_war=parse_bool_or_none(body.get_scalar("break_on_war")),
                break_on_becoming_subject=parse_bool_or_none(
                    body.get_scalar("break_on_becoming_subject")
                ),
                break_on_not_spying=parse_bool_or_none(
                    body.get_scalar("break_on_not_spying")
                ),
                annulled_by_peace_treaty=parse_bool_or_none(
                    body.get_scalar("annulled_by_peace_treaty")
                ),
                disallow_war=parse_bool_or_none(body.get_scalar("disallow_war")),
                embargo=parse_bool_or_none(body.get_scalar("embargo")),
                military_access=parse_bool_or_none(body.get_scalar("military_access")),
                fleet_basing_rights=parse_bool_or_none(
                    body.get_scalar("fleet_basing_rights")
                ),
                food_access=parse_bool_or_none(body.get_scalar("food_access")),
                is_exempt_from_sound_toll=parse_bool_or_none(
                    body.get_scalar("is_exempt_from_sound_toll")
                ),
                is_exempt_from_isolation=parse_bool_or_none(
                    body.get_scalar("is_exempt_from_isolation")
                ),
                block_building=parse_bool_or_none(body.get_scalar("block_building")),
                skip_diplomat_for_cancel=parse_bool_or_none(
                    body.get_scalar("skip_diplomat_for_cancel")
                ),
                lifts_fog_of_war=parse_bool_or_none(body.get_scalar("lifts_fog_of_war")),
                lifts_trade_protection=parse_bool_or_none(
                    body.get_scalar("lifts_trade_protection")
                ),
                show_break_alert=parse_bool_or_none(body.get_scalar("show_break_alert")),
                is_ongoing=parse_bool_or_none(body.get_scalar("is_ongoing")),
                can_share_maps=parse_bool_or_none(body.get_scalar("can_share_maps")),
                category=body.get_object("category"),
                visible=body.get_object("visible"),
                offer_visible=body.get_object("offer_visible"),
                request_visible=body.get_object("request_visible"),
                cancel_visible=body.get_object("cancel_visible"),
                break_visible=body.get_object("break_visible"),
                offer_enabled=body.get_object("offer_enabled"),
                request_enabled=body.get_object("request_enabled"),
                cancel_enabled=body.get_object("cancel_enabled"),
                break_enabled=body.get_object("break_enabled"),
                will_expire_trigger=body.get_object("will_expire_trigger"),
                should_ai_offer_trigger=body.get_object("should_ai_offer_trigger"),
                wants_to_give=body.get_object("wants_to_give"),
                wants_to_receive=body.get_object("wants_to_receive"),
                wants_to_give_diplo_chance=body.get_object("wants_to_give_diplo_chance"),
                wants_to_receive_diplo_chance=body.get_object(
                    "wants_to_receive_diplo_chance"
                ),
                wants_to_keep=body.get_object("wants_to_keep"),
                wants_to_keep_diplo_chance=body.get_object("wants_to_keep_diplo_chance"),
                giving_modifier_scale=body.get_object("giving_modifier_scale"),
                receiving_modifier_scale=body.get_object("receiving_modifier_scale"),
                mutual_modifier_scale=body.get_object("mutual_modifier_scale"),
                offer_effect=body.get_object("offer_effect"),
                request_effect=body.get_object("request_effect"),
                cancel_effect=body.get_object("cancel_effect"),
                break_effect=body.get_object("break_effect"),
                offer_declined_effect=body.get_object("offer_declined_effect"),
                request_declined_effect=body.get_object("request_declined_effect"),
                expire_effect=body.get_object("expire_effect"),
                progress=body.get_object("progress"),
                entry=entry,
            )
        )

    return ScriptedRelationDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )
