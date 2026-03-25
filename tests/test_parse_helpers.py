from __future__ import annotations

from eu5miner.domains._parse_helpers import (
    body_value_text,
    document_child_keys,
    entry_object,
    entry_scalar_text,
    entry_value_text,
    object_child_keys,
    parse_bool_or_none,
    parse_float_or_none,
    parse_int_or_none,
)
from eu5miner.formats.semantic import parse_semantic_document


def test_scalar_coercion_helpers() -> None:
    assert parse_bool_or_none("yes") is True
    assert parse_bool_or_none("false") is False
    assert parse_bool_or_none("maybe") is None
    assert parse_int_or_none("12") == 12
    assert parse_int_or_none(None) is None
    assert parse_float_or_none("0.25") == 0.25
    assert parse_float_or_none(None) is None


def test_semantic_access_helpers() -> None:
    document = parse_semantic_document(
        "root = {\n"
        "    tags = { alpha beta }\n"
        "    stance = friendly\n"
        "    color = rgb { 1 2 3 }\n"
        "}\n"
        "volcanoes = { loc_a loc_b }\n"
    )

    root_entry = document.first_entry("root")
    assert root_entry is not None

    root = entry_object(root_entry)
    assert root is not None
    assert object_child_keys(root, "tags") == ("alpha", "beta")
    assert body_value_text(root, "stance") == "friendly"
    assert body_value_text(root, "color") == "rgb"
    assert entry_scalar_text(root.first_entry("stance")) == "friendly"
    assert entry_value_text(root.first_entry("color")) == "rgb"
    assert document_child_keys(document, "volcanoes") == ("loc_a", "loc_b")
