"""Typed helpers for EU5 map CSV tables such as adjacencies and ports."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import parse_int_or_none
from eu5miner.formats.map_csv import parse_semicolon_csv


@dataclass(frozen=True)
class MapAdjacencyDefinition:
    """One adjacency row from adjacencies.csv."""

    from_location: str
    to_location: str
    adjacency_type: str
    through: str | None
    start_x: int | None
    start_y: int | None
    stop_x: int | None
    stop_y: int | None
    comment: str | None
    row: dict[str, str]


@dataclass(frozen=True)
class MapAdjacencyDocument:
    """Parsed adjacencies.csv table."""

    definitions: tuple[MapAdjacencyDefinition, ...]

    def connections(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            (definition.from_location, definition.to_location)
            for definition in self.definitions
        )

    def get_connection(
        self,
        from_location: str,
        to_location: str,
    ) -> MapAdjacencyDefinition | None:
        for definition in self.definitions:
            if definition.from_location == from_location and definition.to_location == to_location:
                return definition
        return None


@dataclass(frozen=True)
class MapPortDefinition:
    """One port row from ports.csv."""

    land_province: str
    sea_zone: str
    x: int | None
    y: int | None
    marker: str | None
    row: dict[str, str]


@dataclass(frozen=True)
class MapPortDocument:
    """Parsed ports.csv table."""

    definitions: tuple[MapPortDefinition, ...]

    def land_provinces(self) -> tuple[str, ...]:
        return tuple(definition.land_province for definition in self.definitions)

    def get_port(self, land_province: str) -> MapPortDefinition | None:
        for definition in self.definitions:
            if definition.land_province == land_province:
                return definition
        return None


def parse_map_adjacencies_document(text: str) -> MapAdjacencyDocument:
    rows = parse_semicolon_csv(text)
    return MapAdjacencyDocument(
        definitions=tuple(
            MapAdjacencyDefinition(
                from_location=row["From"],
                to_location=row["To"],
                adjacency_type=row["Type"],
                through=_none_if_empty(row.get("Through")),
                start_x=_parse_optional_int(row.get("start_x")),
                start_y=_parse_optional_int(row.get("start_y")),
                stop_x=_parse_optional_int(row.get("stop_x")),
                stop_y=_parse_optional_int(row.get("stop_y")),
                comment=_none_if_empty(row.get("Comment")),
                row=row,
            )
            for row in rows
        )
    )


def parse_map_ports_document(text: str) -> MapPortDocument:
    rows = parse_semicolon_csv(text)
    return MapPortDocument(
        definitions=tuple(
            MapPortDefinition(
                land_province=row["LandProvince"],
                sea_zone=row["SeaZone"],
                x=_parse_optional_int(row.get("x")),
                y=_parse_optional_int(row.get("y")),
                marker=_none_if_empty(row.get("")),
                row=row,
            )
            for row in rows
        )
    )


def _parse_optional_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    return parse_int_or_none(value)


def _none_if_empty(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    return value
