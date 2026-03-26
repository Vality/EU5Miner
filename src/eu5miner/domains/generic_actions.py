"""Domain adapter for generic action definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.interfaces import get_by_name, names_from_named
from eu5miner.domains._macros import collect_parameters_from_object
from eu5miner.domains._parse_helpers import parse_bool_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
    parse_semantic_document,
)


@dataclass(frozen=True)
class GenericActionColumn:
    """One column definition inside a generic action select trigger."""

    data: str | None
    width: str | None
    icon: str | None
    show_icon_in_cells: bool | None
    body: SemanticObject
    entry: SemanticEntry


@dataclass(frozen=True)
class GenericActionSelectTrigger:
    """One select_trigger block inside a generic action."""

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
    allow_null: bool | SemanticObject | None
    allow_self: bool | None
    move_to_next_section_on_click: bool | None
    top_widget: str | None
    bottom_widget: str | None
    columns: tuple[GenericActionColumn, ...]
    default_sort: str | None
    tooltip_msg_key: str | None
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
    ai_override_value: str | None
    map_mode: str | None
    map_color: str | None
    secondary_map_color: str | None
    interaction_source_list: SemanticObject | None
    ai_interaction_source_list: SemanticObject | None
    entry: SemanticEntry


@dataclass(frozen=True)
class GenericActionDefinition:
    """One generic action definition."""

    name: str
    body: SemanticObject
    action_type: str | None
    sound: str | None
    message: str | None
    potential: SemanticObject | None
    allow: SemanticObject | None
    ai_prerequisite: SemanticObject | None
    price: str | None
    price_modifier: SemanticObject | None
    payer: str | None
    payee: str | None
    select_triggers: tuple[GenericActionSelectTrigger, ...]
    ai_tick: str | None
    ai_tick_frequency: str | None
    automation_tick: str | None
    automation_tick_frequency: str | None
    show_message: bool | None
    show_message_to_target: bool | None
    should_execute_price: bool | None
    show_in_gui_list: bool | None
    ai_will_do: SemanticObject | None
    player_automated_category: str | None
    effect: SemanticObject | None
    cooldown: SemanticObject | None
    maximum_targets_in_one_tick: str | None
    force_click_and_confirm_or_hold: bool | None
    parameters: tuple[str, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class GenericActionDocument:
    """Parsed generic action file."""

    definitions: tuple[GenericActionDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return names_from_named(self.definitions)

    def get_definition(self, name: str) -> GenericActionDefinition | None:
        return get_by_name(self.definitions, name)


def parse_generic_action_document(text: str) -> GenericActionDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[GenericActionDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            GenericActionDefinition(
                name=entry.key,
                body=body,
                action_type=body.get_scalar("type"),
                sound=body.get_scalar("sound"),
                message=body.get_scalar("message"),
                potential=body.get_object("potential"),
                allow=body.get_object("allow"),
                ai_prerequisite=body.get_object("ai_prerequisite"),
                price=body.get_scalar("price"),
                price_modifier=body.get_object("price_modifier"),
                payer=body.get_scalar("payer"),
                payee=body.get_scalar("payee"),
                select_triggers=_parse_select_triggers(body),
                ai_tick=body.get_scalar("ai_tick"),
                ai_tick_frequency=body.get_scalar("ai_tick_frequency"),
                automation_tick=body.get_scalar("automation_tick"),
                automation_tick_frequency=body.get_scalar("automation_tick_frequency"),
                show_message=parse_bool_or_none(body.get_scalar("show_message")),
                show_message_to_target=parse_bool_or_none(
                    body.get_scalar("show_message_to_target")
                ),
                should_execute_price=parse_bool_or_none(
                    body.get_scalar("should_execute_price")
                ),
                show_in_gui_list=parse_bool_or_none(body.get_scalar("show_in_gui_list")),
                ai_will_do=body.get_object("ai_will_do"),
                player_automated_category=body.get_scalar("player_automated_category"),
                effect=body.get_object("effect"),
                cooldown=body.get_object("cooldown"),
                maximum_targets_in_one_tick=body.get_scalar("maximum_targets_in_one_tick"),
                force_click_and_confirm_or_hold=parse_bool_or_none(
                    body.get_scalar("force_click_and_confirm_or_hold")
                ),
                parameters=tuple(sorted(collect_parameters_from_object(body))),
                entry=entry,
            )
        )

    return GenericActionDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_select_triggers(body: SemanticObject) -> tuple[GenericActionSelectTrigger, ...]:
    select_triggers: list[GenericActionSelectTrigger] = []

    for entry in body.find_entries("select_trigger"):
        if not isinstance(entry.value, SemanticObject):
            continue

        trigger_body = entry.value
        select_triggers.append(
            GenericActionSelectTrigger(
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
                allow_null=_parse_bool_or_object(trigger_body.first_entry("allow_null")),
                allow_self=parse_bool_or_none(trigger_body.get_scalar("allow_self")),
                move_to_next_section_on_click=parse_bool_or_none(
                    trigger_body.get_scalar("move_to_next_section_on_click")
                ),
                top_widget=trigger_body.get_scalar("top_widget"),
                bottom_widget=trigger_body.get_scalar("bottom_widget"),
                columns=_parse_columns(trigger_body),
                default_sort=trigger_body.get_scalar("default_sort"),
                tooltip_msg_key=trigger_body.get_scalar("tooltip_msg_key"),
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
                ai_override_value=trigger_body.get_scalar("ai_override_value"),
                map_mode=trigger_body.get_scalar("map_mode"),
                map_color=trigger_body.get_scalar("map_color"),
                secondary_map_color=trigger_body.get_scalar("secondary_map_color"),
                interaction_source_list=trigger_body.get_object("interaction_source_list"),
                ai_interaction_source_list=trigger_body.get_object("ai_interaction_source_list"),
                entry=entry,
            )
        )

    return tuple(select_triggers)


def _parse_columns(trigger_body: SemanticObject) -> tuple[GenericActionColumn, ...]:
    columns: list[GenericActionColumn] = []

    for entry in trigger_body.find_entries("column"):
        if not isinstance(entry.value, SemanticObject):
            continue

        column_body = entry.value
        columns.append(
            GenericActionColumn(
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


def _parse_bool_or_object(entry: SemanticEntry | None) -> bool | SemanticObject | None:
    if entry is None:
        return None
    if isinstance(entry.value, SemanticObject):
        return entry.value
    if isinstance(entry.value, SemanticScalar):
        return parse_bool_or_none(entry.value.text)
    return None
