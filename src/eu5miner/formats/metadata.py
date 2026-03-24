"""JSON metadata reader for DLC and future mod metadata files."""

from __future__ import annotations

import json
from typing import Any


def parse_metadata_json(text: str) -> dict[str, Any]:
    data = json.loads(text.removeprefix("\ufeff"))
    if not isinstance(data, dict):
        raise ValueError("Metadata JSON must decode to an object")
    return data
