"""Domain adapter for character interaction definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
    entry_object,
    entry_scalar_text,
    parse_bool_or_none,
)
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)


@dataclass(frozen=True)
class CharacterInteractionColumn:
    data: str | None
    width: str | None
    icon: str | None
    show_icon_in_cells: bool | None
    body: SemanticObject
    entry: SemanticEntry


@dataclass(frozen=True)
class CharacterInteractionSelectTrigger:
    body: SemanticObject
    looking_for_a: str | None
    target_flag: str | None
    source: str | None
    source_ai_override: str | None
    source_flags: tuple[str, ...]
    source_flags_ai_override: tuple[str, ...]
    source_global_list: str | None
    pre_evaluation_sort_value: str | None
    pre_evaluation_number_to_evaluate_fully: str | None
    max_targets_for_ui: str | None
    cache_targets: bool | None
    cache_interaction_source_list: bool | None
    cache_order: bool | None
    name: str | None
    allow_null: bool | None
    allow_null_trigger: SemanticObject | None
    allow_self: bool | None
    move_to_next_section_on_click: bool | None
    top_widget: str | None
    bottom_widget: str | None
    columns: tuple[CharacterInteractionColumn, ...]
    default_sort: str | None
    none_available_msg_key: str | None
    show_why_not_visible: bool | None
    show_why_not_enabled: bool | None
    show_if: SemanticObject | None
    visible: SemanticObject | None
    enabled: SemanticObject | None
    selected: SemanticObject | None
    min_value: str | None
    max_value: str | None
    step: str | None
    default: str | None
    map_mode: str | None
    map_color: str | None
    only_color_selectable: bool | None
    secondary_map_color: str | None
    interaction_source_list: SemanticObject | None
    ai_interaction_source_list: SemanticObject | None
    entry: SemanticEntry


@dataclass(frozen=True)
class CharacterInteractionDefinition:
    name: str
    body: SemanticObject
    message: bool | None
    sound: str | None
    on_other_nation: bool | None
    on_own_nation: bool | None
    is_consort_action: bool | None
    potential: SemanticObject | None
    allow: SemanticObject | None
    price: str | None
    price_modifier: SemanticObject | None
    payer: str | None
    payee: str | None
    select_triggers: tuple[CharacterInteractionSelectTrigger, ...]
    ai_tick: str | None
    ai_tick_frequency: str | None
    show_message: bool | None
    show_message_to_target: bool | None
    should_execute_price: bool | None
    show_in_gui_list: bool | None
    ai_will_do: str | SemanticObject | None
    effect: SemanticObject | None
    cooldown: SemanticObject | None
    context_menu_click_mode: str | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class CharacterInteractionDocument:
    definitions: tuple[CharacterInteractionDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> CharacterInteractionDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_character_interaction_document(text: str) -> CharacterInteractionDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[CharacterInteractionDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue
        body = entry.value
        definitions.append(
            CharacterInteractionDefinition(
                name=entry.key,
                body=body,
                message=parse_bool_or_none(body.get_scalar("message")),
                sound=body.get_scalar("sound"),
                on_other_nation=parse_bool_or_none(body.get_scalar("on_other_nation")),
                on_own_nation=parse_bool_or_none(body.get_scalar("on_own_nation")),
                is_consort_action=parse_bool_or_none(body.get_scalar("is_consort_action")),
                potential=body.get_object("potential"),
                allow=body.get_object("allow"),
                price=body.get_scalar("price"),
                price_modifier=body.get_object("price_modifier"),
                payer=body.get_scalar("payer"),
                payee=body.get_scalar("payee"),
                select_triggers=_parse_select_triggers(body),
                ai_tick=body.get_scalar("ai_tick"),
                ai_tick_frequency=body.get_scalar("ai_tick_frequency"),
                show_message=parse_bool_or_none(body.get_scalar("show_message")),
                show_message_to_target=parse_bool_or_none(
                    body.get_scalar("show_message_to_target")
                ),
                should_execute_price=parse_bool_or_none(
                    body.get_scalar("should_execute_price")
                ),
                show_in_gui_list=parse_bool_or_none(body.get_scalar("show_in_gui_list")),
                ai_will_do=_parse_scalar_or_object(body.first_entry("ai_will_do")),
                effect=body.get_object("effect"),
                cooldown=body.get_object("cooldown"),
                context_menu_click_mode=body.get_scalar("context_menu_click_mode"),
                entry=entry,
            )
        )

    return CharacterInteractionDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_select_triggers(body: SemanticObject) -> tuple[CharacterInteractionSelectTrigger, ...]:
    select_triggers: list[CharacterInteractionSelectTrigger] = []
    for entry in body.find_entries("select_trigger"):
        if not isinstance(entry.value, SemanticObject):
            continue
        trigger_body = entry.value
        select_triggers.append(
            CharacterInteractionSelectTrigger(
                body=trigger_body,
                looking_for_a=trigger_body.get_scalar("looking_for_a"),
                target_flag=trigger_body.get_scalar("target_flag"),
                source=trigger_body.get_scalar("source"),
                source_ai_override=trigger_body.get_scalar("source_ai_override"),
                source_flags=_collect_scalar_like_values(trigger_body.first_entry("source_flags")),
                source_flags_ai_override=_collect_scalar_like_values(
                    trigger_body.first_entry("source_flags_ai_override")
                ),
                source_global_list=trigger_body.get_scalar("source_global_list"),
                pre_evaluation_sort_value=trigger_body.get_scalar("pre_evaluation_sort_value"),
                pre_evaluation_number_to_evaluate_fully=trigger_body.get_scalar(
                    "pre_evaluation_number_to_evaluate_fully"
                ),
                max_targets_for_ui=trigger_body.get_scalar("max_targets_for_ui"),
                cache_targets=parse_bool_or_none(trigger_body.get_scalar("cache_targets")),
                cache_interaction_source_list=parse_bool_or_none(
                    trigger_body.get_scalar("cache_interaction_source_list")
                ),
                cache_order=parse_bool_or_none(trigger_body.get_scalar("cache_order")),
                name=trigger_body.get_scalar("name"),
                allow_null=parse_bool_or_none(trigger_body.get_scalar("allow_null")),
                allow_null_trigger=trigger_body.get_object("allow_null_trigger"),
                allow_self=parse_bool_or_none(trigger_body.get_scalar("allow_self")),
                move_to_next_section_on_click=parse_bool_or_none(
                    trigger_body.get_scalar("move_to_next_section_on_click")
                ),
                top_widget=trigger_body.get_scalar("top_widget"),
                bottom_widget=trigger_body.get_scalar("bottom_widget"),
                columns=_parse_columns(trigger_body),
                default_sort=trigger_body.get_scalar("default_sort"),
                none_available_msg_key=trigger_body.get_scalar("none_available_msg_key"),
                show_why_not_visible=parse_bool_or_none(
                    trigger_body.get_scalar("show_why_not_visible")
                ),
                show_why_not_enabled=parse_bool_or_none(
                    trigger_body.get_scalar("show_why_not_enabled")
                ),
                show_if=trigger_body.get_object("show_if"),
                visible=trigger_body.get_object("visible"),
                enabled=trigger_body.get_object("enabled"),
                selected=trigger_body.get_object("selected"),
                min_value=trigger_body.get_scalar("min"),
                max_value=trigger_body.get_scalar("max"),
                step=trigger_body.get_scalar("step"),
                default=trigger_body.get_scalar("default"),
                map_mode=trigger_body.get_scalar("map_mode"),
                map_color=trigger_body.get_scalar("map_color"),
                only_color_selectable=parse_bool_or_none(
                    trigger_body.get_scalar("only_color_selectable")
                ),
                secondary_map_color=trigger_body.get_scalar("secondary_map_color"),
                interaction_source_list=trigger_body.get_object("interaction_source_list"),
                ai_interaction_source_list=trigger_body.get_object("ai_interaction_source_list"),
                entry=entry,
            )
        )
    return tuple(select_triggers)


def _parse_columns(trigger_body: SemanticObject) -> tuple[CharacterInteractionColumn, ...]:
    columns: list[CharacterInteractionColumn] = []
    for entry in trigger_body.find_entries("column"):
        if not isinstance(entry.value, SemanticObject):
            continue
        column_body = entry.value
        columns.append(
            CharacterInteractionColumn(
                data=column_body.get_scalar("data"),
                width=column_body.get_scalar("width"),
                icon=column_body.get_scalar("icon"),
                show_icon_in_cells=parse_bool_or_none(
                    column_body.get_scalar("show_icon_in_cells")
                ),
                body=column_body,
                entry=entry,
            )
        )
    return tuple(columns)


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