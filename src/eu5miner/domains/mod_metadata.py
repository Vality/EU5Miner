"""Typed helpers for DLC and mod metadata files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from eu5miner.formats.metadata import parse_metadata_json


@dataclass(frozen=True)
class ModRelationship:
    """One relationship entry from mod metadata."""

    raw: dict[str, Any]

    @property
    def relationship_type(self) -> str | None:
        value = self.raw.get("type")
        return value if isinstance(value, str) else None

    @property
    def target_id(self) -> str | None:
        for key in ("id", "target_id", "mod_id"):
            value = self.raw.get(key)
            if isinstance(value, str):
                return value
        return None


@dataclass(frozen=True)
class ModMetadataDocument:
    """Structured view of DLC or mod metadata.json content."""

    raw: dict[str, Any]
    name: str | None
    localizable_name: str | None
    mod_id: str | None
    version: str | None
    path: str | None
    picture: str | None
    checksum: str | None
    description: str | None
    short_description: str | None
    supported_version: str | None
    supported_game_version: str | None
    dependencies: tuple[str, ...]
    replace_paths: tuple[str, ...]
    tags: tuple[str, ...]
    relationships: tuple[ModRelationship, ...]
    game_custom_data: dict[str, Any] | None
    pops_id: str | None
    msgr_id: str | None
    steam_id: int | None
    review_steam_id: int | None
    affects_save_compatibility: bool | None
    mp_synced: bool | None
    third_party_content: bool | None
    enabled: bool | None
    hidden: bool | None
    verify: bool | None

    def has_relationships(self) -> bool:
        return bool(self.relationships)


def parse_mod_metadata_document(text: str) -> ModMetadataDocument:
    raw = parse_metadata_json(text)

    return ModMetadataDocument(
        raw=raw,
        name=_string_or_none(raw.get("name")),
        localizable_name=_string_or_none(raw.get("localizable_name")),
        mod_id=_string_or_none(raw.get("id")),
        version=_string_or_none(raw.get("version")),
        path=_string_or_none(raw.get("path")),
        picture=_string_or_none(raw.get("picture")),
        checksum=_string_or_none(raw.get("checksum")),
        description=_string_or_none(raw.get("description")),
        short_description=_string_or_none(raw.get("short_description")),
        supported_version=_string_or_none(raw.get("supported_version")),
        supported_game_version=_string_or_none(raw.get("supported_game_version")),
        dependencies=_string_tuple(raw.get("dependencies")),
        replace_paths=_string_tuple(raw.get("replace_path")),
        tags=_string_tuple(raw.get("tags")),
        relationships=_relationship_tuple(raw.get("relationships")),
        game_custom_data=_dict_or_none(raw.get("game_custom_data")),
        pops_id=_string_or_none(raw.get("pops_id")),
        msgr_id=_string_or_none(raw.get("msgr_id")),
        steam_id=_int_or_none(raw.get("steam_id")),
        review_steam_id=_int_or_none(raw.get("review_steam_id")),
        affects_save_compatibility=_bool_or_none(raw.get("affects_save_compatibility")),
        mp_synced=_bool_or_none(raw.get("mp_synced")),
        third_party_content=_bool_or_none(raw.get("third_party_content")),
        enabled=_bool_or_none(raw.get("enabled")),
        hidden=_bool_or_none(raw.get("hidden")),
        verify=_bool_or_none(raw.get("verify")),
    )


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _int_or_none(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _bool_or_none(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _dict_or_none(value: object) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    return value


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _relationship_tuple(value: object) -> tuple[ModRelationship, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(ModRelationship(raw=item) for item in value if isinstance(item, dict))
