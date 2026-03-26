"""Shared parsing helpers for domain adapters."""

from __future__ import annotations

from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    SemanticScalar,
)


def parse_bool_or_none(value: str | None) -> bool | None:
    if value is None:
        return None

    normalized = value.lower()
    if normalized in {"yes", "true"}:
        return True
    if normalized in {"no", "false"}:
        return False
    return None


def parse_int_or_none(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def parse_float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    return float(value)


def entry_scalar_text(entry: SemanticEntry | None) -> str | None:
    if entry is None or not isinstance(entry.value, SemanticScalar):
        return None
    return entry.value.text


def entry_object(entry: SemanticEntry | None) -> SemanticObject | None:
    if entry is None or not isinstance(entry.value, SemanticObject):
        return None
    return entry.value


def entry_value_text(entry: SemanticEntry | None) -> str | None:
    scalar_text = entry_scalar_text(entry)
    if scalar_text is not None:
        return scalar_text

    value_object = entry_object(entry)
    if value_object is not None:
        return value_object.prefix or None
    return None


def body_value_text(body: SemanticObject, key: str) -> str | None:
    return entry_value_text(body.first_entry(key))


def collect_scalar_entries(body: SemanticObject, key: str) -> tuple[str, ...]:
    return tuple(
        entry.value.text
        for entry in body.find_entries(key)
        if isinstance(entry.value, SemanticScalar)
    )


def collect_scalar_like_values(entry: SemanticEntry | None) -> tuple[str, ...]:
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


def object_child_keys(body: SemanticObject, key: str) -> tuple[str, ...]:
    value = body.get_object(key)
    if value is None:
        return ()
    return tuple(entry.key for entry in value.entries)


def document_child_keys(document: SemanticDocument, key: str) -> tuple[str, ...]:
    value = entry_object(document.first_entry(key))
    if value is None:
        return ()
    return tuple(entry.key for entry in value.entries)
