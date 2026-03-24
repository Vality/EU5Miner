"""Semicolon-delimited CSV reader."""

from __future__ import annotations

import csv
from io import StringIO


def parse_semicolon_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(StringIO(text), delimiter=";")
    return [dict(row) for row in reader]
