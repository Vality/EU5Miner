"""Domain adapter for EU5 map text files such as default.map."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import (
    document_child_keys,
    entry_scalar_text,
    parse_bool_or_none,
    parse_int_or_none,
)
from eu5miner.formats import semantic


@dataclass(frozen=True)
class DefaultMapReferencedFiles:
    """Referenced file names from a parsed default.map document."""

    provinces: str | None
    rivers: str | None
    topology: str | None
    adjacencies: str | None
    setup: str | None
    ports: str | None
    location_templates: str | None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "provinces": self.provinces,
            "rivers": self.rivers,
            "topology": self.topology,
            "adjacencies": self.adjacencies,
            "setup": self.setup,
            "ports": self.ports,
            "location_templates": self.location_templates,
        }


@dataclass(frozen=True)
class SoundTollDefinition:
    """One sound-toll mapping in default.map."""

    name: str
    location: str | None
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class DefaultMapDocument:
    """Parsed default.map structure."""

    referenced_files: DefaultMapReferencedFiles
    equator_y: int | None
    wrap_x: bool | None
    sound_tolls: tuple[SoundTollDefinition, ...]
    volcanoes: tuple[str, ...]
    earthquakes: tuple[str, ...]
    sea_zones: tuple[str, ...]
    lakes: tuple[str, ...]
    impassable_mountains: tuple[str, ...]
    non_ownable: tuple[str, ...]
    semantic_document: semantic.SemanticDocument

    def get_sound_toll(self, name: str) -> SoundTollDefinition | None:
        for definition in self.sound_tolls:
            if definition.name == name:
                return definition
        return None


def parse_default_map_document(text: str) -> DefaultMapDocument:
    semantic_document = semantic.parse_semantic_document(text)

    return DefaultMapDocument(
        referenced_files=DefaultMapReferencedFiles(
            provinces=_get_scalar(semantic_document, "provinces"),
            rivers=_get_scalar(semantic_document, "rivers"),
            topology=_get_scalar(semantic_document, "topology"),
            adjacencies=_get_scalar(semantic_document, "adjacencies"),
            setup=_get_scalar(semantic_document, "setup"),
            ports=_get_scalar(semantic_document, "ports"),
            location_templates=_get_scalar(semantic_document, "location_templates"),
        ),
        equator_y=parse_int_or_none(_get_scalar(semantic_document, "equator_y")),
        wrap_x=parse_bool_or_none(_get_scalar(semantic_document, "wrap_x")),
        sound_tolls=_parse_sound_tolls(semantic_document),
        volcanoes=document_child_keys(semantic_document, "volcanoes"),
        earthquakes=document_child_keys(semantic_document, "earthquakes"),
        sea_zones=document_child_keys(semantic_document, "sea_zones"),
        lakes=document_child_keys(semantic_document, "lakes"),
        impassable_mountains=document_child_keys(semantic_document, "impassable_mountains"),
        non_ownable=document_child_keys(semantic_document, "non_ownable"),
        semantic_document=semantic_document,
    )


def _get_scalar(document: semantic.SemanticDocument, key: str) -> str | None:
    entry = document.first_entry(key)
    if entry is None or not isinstance(entry.value, semantic.SemanticScalar):
        return None
    return entry.value.text


def _is_scalar_entry(entry: semantic.SemanticEntry | None) -> bool:
    return entry is not None and isinstance(entry.value, semantic.SemanticScalar)


def _parse_sound_tolls(
    document: semantic.SemanticDocument,
) -> tuple[SoundTollDefinition, ...]:
    sound_toll_object = _get_object(document, "sound_toll")
    if sound_toll_object is None:
        return ()

    return tuple(
        SoundTollDefinition(
            name=entry.key,
            location=entry_scalar_text(entry),
            entry=entry,
        )
        for entry in sound_toll_object.entries
    )


def _get_object(document: semantic.SemanticDocument, key: str) -> semantic.SemanticObject | None:
    entry = document.first_entry(key)
    if entry is None or not isinstance(entry.value, semantic.SemanticObject):
        return None
    return entry.value
