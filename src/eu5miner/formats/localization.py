"""Localization reader for Paradox YAML-like files."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalizationEntry:
    key: str
    value: str


@dataclass(frozen=True)
class LocalizationFile:
    language: str
    entries: tuple[LocalizationEntry, ...]


def parse_localization(text: str) -> LocalizationFile:
    language = ""
    entries: list[LocalizationEntry] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if not language and line.startswith("l_") and line.endswith(":"):
            language = line[:-1]
            continue

        if ":" not in raw_line:
            continue

        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            continue

        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            value = value[1:-1]
        entries.append(LocalizationEntry(key=key, value=value))

    if not language:
        raise ValueError("Localization file is missing a language header")

    return LocalizationFile(language=language, entries=tuple(entries))
