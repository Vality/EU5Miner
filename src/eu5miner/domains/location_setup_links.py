"""Helpers for cross-linking map locations with setup data."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats import semantic

COUNTRY_LOCATION_CATEGORIES = (
    "own_control_core",
    "own_control_integrated",
    "own_control_conquered",
    "own_control_colony",
    "own_core",
    "own_conquered",
    "own_integrated",
    "own_colony",
    "control_core",
    "control",
    "our_cores_conquered_by_others",
)


@dataclass(frozen=True)
class LocationHierarchyDefinition:
    """One location name resolved from definitions.txt with its hierarchy path."""

    name: str
    hierarchy_path: tuple[str, ...]

    @property
    def leaf_group(self) -> str | None:
        if not self.hierarchy_path:
            return None
        return self.hierarchy_path[-1]


@dataclass(frozen=True)
class LocationHierarchyDocument:
    """Parsed location hierarchy from definitions.txt."""

    definitions: tuple[LocationHierarchyDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_location(self, name: str) -> LocationHierarchyDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


@dataclass(frozen=True)
class CountryLocationGroup:
    """One location list category for a country in 10_countries.txt."""

    category: str
    locations: tuple[str, ...]


@dataclass(frozen=True)
class CountryLocationDefinition:
    """Country-side location references from 10_countries.txt."""

    tag: str
    capital: str | None
    location_groups: tuple[CountryLocationGroup, ...]
    body: semantic.SemanticObject
    entry: semantic.SemanticEntry

    def get_locations(self, category: str) -> tuple[str, ...]:
        for group in self.location_groups:
            if group.category == category:
                return group.locations
        return ()


@dataclass(frozen=True)
class CountryLocationDocument:
    """Parsed country-side location references."""

    definitions: tuple[CountryLocationDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def tags(self) -> tuple[str, ...]:
        return tuple(definition.tag for definition in self.definitions)

    def get_definition(self, tag: str) -> CountryLocationDefinition | None:
        for definition in self.definitions:
            if definition.tag == tag:
                return definition
        return None


@dataclass(frozen=True)
class LocationSetupDefinition:
    """One per-location setup definition from 21_locations.txt."""

    name: str
    body: semantic.SemanticObject
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class LocationSetupDocument:
    """Parsed location setup definitions."""

    definitions: tuple[LocationSetupDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> LocationSetupDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


@dataclass(frozen=True)
class LocationCountryReference:
    """One country-to-location reference after cross-linking."""

    country_tag: str
    category: str


@dataclass(frozen=True)
class LinkedLocationDefinition:
    """Merged location index entry across hierarchy, country setup, and location setup."""

    name: str
    hierarchy: LocationHierarchyDefinition | None
    country_references: tuple[LocationCountryReference, ...]
    capital_of: tuple[str, ...]
    location_setup: LocationSetupDefinition | None

    @property
    def has_location_setup(self) -> bool:
        return self.location_setup is not None


@dataclass(frozen=True)
class LinkedLocationDocument:
    """Cross-linked location index."""

    definitions: tuple[LinkedLocationDefinition, ...]

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_location(self, name: str) -> LinkedLocationDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_location_hierarchy_document(text: str) -> LocationHierarchyDocument:
    semantic_document = semantic.parse_semantic_document(text)
    definitions: list[LocationHierarchyDefinition] = []

    for entry in semantic_document.entries:
        if isinstance(entry.value, semantic.SemanticObject):
            definitions.extend(_collect_location_hierarchy(entry.value, (entry.key,)))

    return LocationHierarchyDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def parse_country_location_document(text: str) -> CountryLocationDocument:
    semantic_document = semantic.parse_semantic_document(text)
    outer_countries = semantic_document.first_entry("countries")
    if outer_countries is None or not isinstance(outer_countries.value, semantic.SemanticObject):
        return CountryLocationDocument(definitions=(), semantic_document=semantic_document)

    inner_countries = outer_countries.value.get_object("countries")
    if inner_countries is None:
        return CountryLocationDocument(definitions=(), semantic_document=semantic_document)

    definitions = tuple(
        _parse_country_location_definition(entry)
        for entry in inner_countries.entries
        if isinstance(entry.value, semantic.SemanticObject)
    )

    return CountryLocationDocument(
        definitions=definitions,
        semantic_document=semantic_document,
    )


def parse_location_setup_document(text: str) -> LocationSetupDocument:
    semantic_document = semantic.parse_semantic_document(text)
    outer_locations = semantic_document.first_entry("locations")
    if outer_locations is None or not isinstance(outer_locations.value, semantic.SemanticObject):
        return LocationSetupDocument(definitions=(), semantic_document=semantic_document)

    definitions = tuple(
        LocationSetupDefinition(name=entry.key, body=entry.value, entry=entry)
        for entry in outer_locations.value.entries
        if isinstance(entry.value, semantic.SemanticObject)
    )
    return LocationSetupDocument(
        definitions=definitions,
        semantic_document=semantic_document,
    )


def build_linked_location_document(
    hierarchy_document: LocationHierarchyDocument,
    country_document: CountryLocationDocument,
    setup_document: LocationSetupDocument,
) -> LinkedLocationDocument:
    hierarchy_by_name = {
        definition.name: definition for definition in hierarchy_document.definitions
    }
    setup_by_name = {definition.name: definition for definition in setup_document.definitions}
    country_refs: dict[str, list[LocationCountryReference]] = {}
    capital_refs: dict[str, list[str]] = {}

    for country in country_document.definitions:
        if country.capital is not None:
            capital_refs.setdefault(country.capital, []).append(country.tag)

        for group in country.location_groups:
            for location in group.locations:
                country_refs.setdefault(location, []).append(
                    LocationCountryReference(country_tag=country.tag, category=group.category)
                )

    all_names = sorted(
        set(hierarchy_by_name)
        | set(setup_by_name)
        | set(country_refs)
        | set(capital_refs)
    )

    return LinkedLocationDocument(
        definitions=tuple(
            LinkedLocationDefinition(
                name=name,
                hierarchy=hierarchy_by_name.get(name),
                country_references=tuple(country_refs.get(name, ())),
                capital_of=tuple(capital_refs.get(name, ())),
                location_setup=setup_by_name.get(name),
            )
            for name in all_names
        )
    )


def _collect_location_hierarchy(
    value: semantic.SemanticObject,
    path: tuple[str, ...],
) -> list[LocationHierarchyDefinition]:
    if _is_leaf_location_group(value):
        return [
            LocationHierarchyDefinition(name=entry.key, hierarchy_path=path)
            for entry in value.entries
        ]

    definitions: list[LocationHierarchyDefinition] = []
    for entry in value.entries:
        if isinstance(entry.value, semantic.SemanticObject):
            definitions.extend(_collect_location_hierarchy(entry.value, path + (entry.key,)))
    return definitions


def _is_leaf_location_group(value: semantic.SemanticObject) -> bool:
    return bool(value.entries) and all(entry.value is None for entry in value.entries)


def _parse_country_location_definition(entry: semantic.SemanticEntry) -> CountryLocationDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    groups = tuple(
        CountryLocationGroup(
            category=category,
            locations=_extract_list_names(entry.value.get_object(category)),
        )
        for category in COUNTRY_LOCATION_CATEGORIES
        if entry.value.get_object(category) is not None
    )

    return CountryLocationDefinition(
        tag=entry.key,
        capital=entry.value.get_scalar("capital"),
        location_groups=groups,
        body=entry.value,
        entry=entry,
    )


def _extract_list_names(value: semantic.SemanticObject | None) -> tuple[str, ...]:
    if value is None:
        return ()
    return tuple(entry.key for entry in value.entries)
