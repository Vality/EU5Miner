"""Domain adapter for attribute column definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import parse_bool_or_none
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class AttributeColumnSortDefinition:
    """One sort block inside an attribute column definition."""

    body: SemanticObject
    sort_text: SemanticObject | None
    sort_value: SemanticObject | None
    sort_by_tooltip_key: str | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class AttributeColumnDefinition:
    """One attribute column definition within an object-type group."""

    name: str
    body: SemanticObject
    widget: str | None
    width: str | None
    fixed_height: str | None
    is_constant_width: bool | None
    contains_select_target_button: bool | None
    single_widget_for_row: bool | None
    sorts: tuple[AttributeColumnSortDefinition, ...]
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class AttributeColumnGroupDefinition:
    """One top-level object-type group such as market or goods."""

    name: str
    body: SemanticObject
    columns: tuple[AttributeColumnDefinition, ...]
    entry: SemanticEntry

    def get_column(self, name: str) -> AttributeColumnDefinition | None:
        for column in self.columns:
            if column.name == name:
                return column
        return None


@dataclass(frozen=True)
class AttributeColumnDocument:
    """Parsed attribute column file."""

    groups: tuple[AttributeColumnGroupDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(group.name for group in self.groups)

    def get_group(self, name: str) -> AttributeColumnGroupDefinition | None:
        for group in self.groups:
            if group.name == name:
                return group
        return None


def parse_attribute_column_document(text: str) -> AttributeColumnDocument:
    semantic_document = parse_semantic_document(text)
    groups: list[AttributeColumnGroupDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        groups.append(
            AttributeColumnGroupDefinition(
                name=entry.key,
                body=entry.value,
                columns=_parse_columns(entry.value),
                entry=entry,
            )
        )

    return AttributeColumnDocument(
        groups=tuple(groups),
        semantic_document=semantic_document,
    )


def _parse_columns(body: SemanticObject) -> tuple[AttributeColumnDefinition, ...]:
    columns: list[AttributeColumnDefinition] = []

    for entry in body.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        column_body = entry.value
        columns.append(
            AttributeColumnDefinition(
                name=entry.key,
                body=column_body,
                widget=column_body.get_scalar("widget"),
                width=column_body.get_scalar("width"),
                fixed_height=column_body.get_scalar("fixed_height"),
                is_constant_width=parse_bool_or_none(column_body.get_scalar("is_constant_width")),
                contains_select_target_button=parse_bool_or_none(
                    column_body.get_scalar("contains_select_target_button")
                ),
                single_widget_for_row=parse_bool_or_none(
                    column_body.get_scalar("single_widget_for_row")
                ),
                sorts=_parse_sorts(column_body),
                entry=entry,
            )
        )

    return tuple(columns)


def _parse_sorts(body: SemanticObject) -> tuple[AttributeColumnSortDefinition, ...]:
    sorts: list[AttributeColumnSortDefinition] = []

    for entry in body.find_entries("sort"):
        if not isinstance(entry.value, SemanticObject):
            continue

        sort_body = entry.value
        sorts.append(
            AttributeColumnSortDefinition(
                body=sort_body,
                sort_text=sort_body.get_object("sort_text"),
                sort_value=sort_body.get_object("sort_value"),
                sort_by_tooltip_key=sort_body.get_scalar("sort_by_tooltip_key"),
                entry=entry,
            )
        )

    return tuple(sorts)
