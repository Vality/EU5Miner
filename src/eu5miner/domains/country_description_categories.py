"""Domain adapter for country description categories and setup-country usage."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.setup_countries import SetupCountryDefinition, SetupCountryDocument
from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class CountryDescriptionCategoryDefinition:
    """One country description category definition."""

    name: str
    body: SemanticObject
    entry: SemanticEntry


@dataclass(frozen=True)
class CountryDescriptionCategoryDocument:
    """Parsed country description category file."""

    definitions: tuple[CountryDescriptionCategoryDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> CountryDescriptionCategoryDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


@dataclass(frozen=True)
class CountryDescriptionAssignment:
    """One setup-country assignment to a description category."""

    country_tag: str
    category_name: str
    category: CountryDescriptionCategoryDefinition | None
    setup_country: SetupCountryDefinition

    @property
    def is_defined(self) -> bool:
        return self.category is not None


@dataclass(frozen=True)
class CountryDescriptionCategoryUsage:
    """One category with all setup countries that reference it."""

    category_name: str
    category: CountryDescriptionCategoryDefinition | None
    country_tags: tuple[str, ...]

    @property
    def is_defined(self) -> bool:
        return self.category is not None


@dataclass(frozen=True)
class CountryDescriptionCategoryUsageDocument:
    """Cross-linked category usage across categories and setup countries."""

    usages: tuple[CountryDescriptionCategoryUsage, ...]
    assignments: tuple[CountryDescriptionAssignment, ...]

    def names(self) -> tuple[str, ...]:
        return tuple(usage.category_name for usage in self.usages)

    def get_usage(self, category_name: str) -> CountryDescriptionCategoryUsage | None:
        for usage in self.usages:
            if usage.category_name == category_name:
                return usage
        return None

    def get_assignment(self, country_tag: str) -> CountryDescriptionAssignment | None:
        for assignment in self.assignments:
            if assignment.country_tag == country_tag:
                return assignment
        return None


def parse_country_description_category_document(text: str) -> CountryDescriptionCategoryDocument:
    semantic_document = parse_semantic_document(text)
    definitions = tuple(
        CountryDescriptionCategoryDefinition(name=entry.key, body=entry.value, entry=entry)
        for entry in semantic_document.entries
        if isinstance(entry.value, SemanticObject)
    )
    return CountryDescriptionCategoryDocument(
        definitions=definitions,
        semantic_document=semantic_document,
    )


def build_country_description_category_usage_document(
    category_document: CountryDescriptionCategoryDocument,
    setup_document: SetupCountryDocument,
) -> CountryDescriptionCategoryUsageDocument:
    categories_by_name = {
        definition.name: definition for definition in category_document.definitions
    }

    assignments = tuple(
        CountryDescriptionAssignment(
            country_tag=definition.tag,
            category_name=definition.description_category,
            category=categories_by_name.get(definition.description_category),
            setup_country=definition,
        )
        for definition in setup_document.definitions
        if definition.description_category is not None
    )

    category_names = sorted(
        set(categories_by_name).union(assignment.category_name for assignment in assignments)
    )

    usages = tuple(
        CountryDescriptionCategoryUsage(
            category_name=name,
            category=categories_by_name.get(name),
            country_tags=tuple(
                assignment.country_tag
                for assignment in assignments
                if assignment.category_name == name
            ),
        )
        for name in category_names
    )

    return CountryDescriptionCategoryUsageDocument(
        usages=usages,
        assignments=assignments,
    )
