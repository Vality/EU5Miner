"""Shared helpers for domain adapters that rely on macro substitution."""

from __future__ import annotations

import re

from eu5miner.formats.semantic import SemanticObject, SemanticScalar

MACRO_NAME_RE = re.compile(r"\$([A-Za-z0-9_]+)\$")


def collect_parameters_from_object(value: SemanticObject) -> set[str]:
    parameters: set[str] = set()

    if value.prefix:
        parameters.update(MACRO_NAME_RE.findall(value.prefix))

    for entry in value.entries:
        parameters.update(MACRO_NAME_RE.findall(entry.key))
        if entry.operator is not None:
            parameters.update(MACRO_NAME_RE.findall(entry.operator))

        child_value = entry.value
        if child_value is None:
            continue
        if isinstance(child_value, SemanticScalar):
            parameters.update(MACRO_NAME_RE.findall(child_value.text))
        if isinstance(child_value, SemanticObject):
            parameters.update(collect_parameters_from_object(child_value))

    return parameters
