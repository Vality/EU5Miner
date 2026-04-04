"""Higher-level helpers over religion-adjacent domain adapters."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from eu5miner.domains.interfaces import NamedDefinitionLike, flatten_definitions, get_by_name
from eu5miner.domains.religion.holy_site_types import (
    HolySiteTypeDefinition,
    HolySiteTypeDocument,
    parse_holy_site_type_document,
)
from eu5miner.domains.religion.holy_sites import (
    HolySiteCatalog,
    HolySiteDefinition,
    HolySiteDocument,
    HolySiteReferenceEdge,
    HolySiteReport,
    build_holy_site_catalog,
    build_holy_site_report,
    parse_holy_site_document,
)
from eu5miner.domains.religion.religions import (
    ReligionDefinition,
    ReligionDocument,
    ReligionOpinion,
    parse_religion_document,
)
from eu5miner.domains.religion.religious_aspects import (
    ReligiousAspectDefinition,
    ReligiousAspectDocument,
    ReligiousAspectOpinion,
    parse_religious_aspect_document,
)
from eu5miner.domains.religion.religious_factions import (
    ReligiousFactionDefinition,
    ReligiousFactionDocument,
    parse_religious_faction_document,
)
from eu5miner.domains.religion.religious_figures import (
    ReligiousFigureDefinition,
    ReligiousFigureDocument,
    parse_religious_figure_document,
)
from eu5miner.domains.religion.religious_focuses import (
    ReligiousFocusDefinition,
    ReligiousFocusDocument,
    parse_religious_focus_document,
)
from eu5miner.domains.religion.religious_schools import (
    ReligiousSchoolDefinition,
    ReligiousSchoolDocument,
    parse_religious_school_document,
)
from eu5miner.formats.semantic import SemanticObject, SemanticScalar


@dataclass(frozen=True)
class ReligionReferenceEdge:
    source_name: str
    referenced_names: tuple[str, ...]


@dataclass(frozen=True)
class ReligionReport:
    religion_aspect_links: tuple[ReligionReferenceEdge, ...]
    religion_faction_links: tuple[ReligionReferenceEdge, ...]
    religion_focus_links: tuple[ReligionReferenceEdge, ...]
    religion_school_links: tuple[ReligionReferenceEdge, ...]
    religion_holy_site_links: tuple[ReligionReferenceEdge, ...]
    religion_figure_links: tuple[ReligionReferenceEdge, ...]
    missing_religious_faction_references: tuple[str, ...]
    missing_religious_focus_references: tuple[str, ...]
    missing_religious_school_references: tuple[str, ...]


@dataclass(frozen=True)
class ReligionCatalog:
    religion_definitions: tuple[ReligionDefinition, ...] = ()
    religious_aspect_definitions: tuple[ReligiousAspectDefinition, ...] = ()
    religious_faction_definitions: tuple[ReligiousFactionDefinition, ...] = ()
    religious_focus_definitions: tuple[ReligiousFocusDefinition, ...] = ()
    religious_school_definitions: tuple[ReligiousSchoolDefinition, ...] = ()
    religious_figure_definitions: tuple[ReligiousFigureDefinition, ...] = ()
    holy_site_definitions: tuple[HolySiteDefinition, ...] = ()

    def get_religion(self, name: str) -> ReligionDefinition | None:
        return get_by_name(self.religion_definitions, name)

    def get_religious_aspect(self, name: str) -> ReligiousAspectDefinition | None:
        return get_by_name(self.religious_aspect_definitions, name)

    def get_religious_faction(self, name: str) -> ReligiousFactionDefinition | None:
        return get_by_name(self.religious_faction_definitions, name)

    def get_religious_focus(self, name: str) -> ReligiousFocusDefinition | None:
        return get_by_name(self.religious_focus_definitions, name)

    def get_religious_school(self, name: str) -> ReligiousSchoolDefinition | None:
        return get_by_name(self.religious_school_definitions, name)

    def get_religious_figure(self, name: str) -> ReligiousFigureDefinition | None:
        return get_by_name(self.religious_figure_definitions, name)

    def get_holy_site(self, name: str) -> HolySiteDefinition | None:
        return get_by_name(self.holy_site_definitions, name)

    def get_religious_aspects_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousAspectDefinition, ...]:
        return tuple(
            definition
            for definition in self.religious_aspect_definitions
            if religion_name in definition.religions
        )

    def get_religious_factions_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousFactionDefinition, ...]:
        religion = self.get_religion(religion_name)
        if religion is None:
            return ()
        return tuple(
            definition
            for definition in self.religious_faction_definitions
            if definition.name in religion.factions
        )

    def get_religious_focuses_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousFocusDefinition, ...]:
        religion = self.get_religion(religion_name)
        if religion is None:
            return ()
        return tuple(
            definition
            for definition in self.religious_focus_definitions
            if definition.name in religion.religious_focuses
        )

    def get_religious_schools_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousSchoolDefinition, ...]:
        religion = self.get_religion(religion_name)
        if religion is None:
            return ()
        explicit_school_names = set(religion.religious_schools)
        return tuple(
            definition
            for definition in self.religious_school_definitions
            if definition.name in explicit_school_names
            or _object_mentions_religion(definition.enabled_for_country, religion)
            or _object_mentions_religion(definition.enabled_for_character, religion)
        )

    def get_religious_figures_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousFigureDefinition, ...]:
        religion = self.get_religion(religion_name)
        if religion is None:
            return ()
        return tuple(
            definition
            for definition in self.religious_figure_definitions
            if _object_mentions_religion(definition.enabled_for_religion, religion)
        )

    def get_holy_sites_for_religion(self, religion_name: str) -> tuple[HolySiteDefinition, ...]:
        return tuple(
            definition
            for definition in self.holy_site_definitions
            if religion_name in definition.religions
        )

    def build_report(self) -> ReligionReport:
        aspect_links = _build_edges_without_resolution(
            self.religion_definitions,
            lambda definition: tuple(
                aspect.name for aspect in self.get_religious_aspects_for_religion(definition.name)
            ),
        )
        faction_links, missing_factions = _build_edges(
            self.religion_definitions,
            lambda definition: definition.factions,
            self.get_religious_faction,
        )
        focus_links, missing_focuses = _build_edges(
            self.religion_definitions,
            lambda definition: definition.religious_focuses,
            self.get_religious_focus,
        )
        school_links = _build_edges_without_resolution(
            self.religion_definitions,
            lambda definition: tuple(
                school.name for school in self.get_religious_schools_for_religion(definition.name)
            ),
        )
        missing_schools = tuple(
            sorted(
                {
                    school_name
                    for definition in self.religion_definitions
                    for school_name in definition.religious_schools
                    if self.get_religious_school(school_name) is None
                }
            )
        )
        holy_site_links = _build_edges_without_resolution(
            self.religion_definitions,
            lambda definition: tuple(
                site.name for site in self.get_holy_sites_for_religion(definition.name)
            ),
        )
        figure_links = _build_edges_without_resolution(
            self.religion_definitions,
            lambda definition: tuple(
                figure.name for figure in self.get_religious_figures_for_religion(definition.name)
            ),
        )
        return ReligionReport(
            religion_aspect_links=aspect_links,
            religion_faction_links=faction_links,
            religion_focus_links=focus_links,
            religion_school_links=school_links,
            religion_holy_site_links=holy_site_links,
            religion_figure_links=figure_links,
            missing_religious_faction_references=missing_factions,
            missing_religious_focus_references=missing_focuses,
            missing_religious_school_references=missing_schools,
        )


def build_religion_catalog(
    religion_documents: Sequence[ReligionDocument],
    religious_aspect_documents: Sequence[ReligiousAspectDocument] = (),
    religious_faction_documents: Sequence[ReligiousFactionDocument] = (),
    religious_focus_documents: Sequence[ReligiousFocusDocument] = (),
    religious_school_documents: Sequence[ReligiousSchoolDocument] = (),
    religious_figure_documents: Sequence[ReligiousFigureDocument] = (),
    holy_site_documents: Sequence[HolySiteDocument] = (),
) -> ReligionCatalog:
    return ReligionCatalog(
        religion_definitions=flatten_definitions(religion_documents),
        religious_aspect_definitions=flatten_definitions(religious_aspect_documents),
        religious_faction_definitions=flatten_definitions(religious_faction_documents),
        religious_focus_definitions=flatten_definitions(religious_focus_documents),
        religious_school_definitions=flatten_definitions(religious_school_documents),
        religious_figure_definitions=flatten_definitions(religious_figure_documents),
        holy_site_definitions=flatten_definitions(holy_site_documents),
    )


def build_religion_report(catalog: ReligionCatalog) -> ReligionReport:
    return catalog.build_report()


def _build_edges[DefinitionT: NamedDefinitionLike](
    definitions: Sequence[DefinitionT],
    collector: Callable[[DefinitionT], tuple[str, ...]],
    resolver: Callable[[str], Any | None],
) -> tuple[tuple[ReligionReferenceEdge, ...], tuple[str, ...]]:
    edges: list[ReligionReferenceEdge] = []
    missing: set[str] = set()

    for definition in definitions:
        source_name = definition.name
        references = tuple(reference for reference in collector(definition) if reference)
        if not references:
            continue
        edges.append(ReligionReferenceEdge(source_name=source_name, referenced_names=references))
        for reference in references:
            if resolver(reference) is None:
                missing.add(reference)

    return tuple(edges), tuple(sorted(missing))


def _build_edges_without_resolution[DefinitionT: NamedDefinitionLike](
    definitions: Sequence[DefinitionT],
    collector: Callable[[DefinitionT], tuple[str, ...]],
) -> tuple[ReligionReferenceEdge, ...]:
    edges: list[ReligionReferenceEdge] = []
    for definition in definitions:
        source_name = definition.name
        references = tuple(reference for reference in collector(definition) if reference)
        if references:
            edges.append(
                ReligionReferenceEdge(source_name=source_name, referenced_names=references)
            )
    return tuple(edges)


def _object_mentions_religion(body: SemanticObject | None, religion: ReligionDefinition) -> bool:
    if body is None:
        return False
    scalar_texts = set(_iter_scalar_texts(body))
    return (
        f"religion:{religion.name}" in scalar_texts
        or (
            religion.group is not None
            and f"religion_group:{religion.group}" in scalar_texts
        )
    )


def _iter_scalar_texts(body: SemanticObject) -> tuple[str, ...]:
    values: list[str] = []
    for entry in body.entries:
        if isinstance(entry.value, SemanticScalar):
            values.append(entry.value.text)
        elif isinstance(entry.value, SemanticObject):
            values.extend(_iter_scalar_texts(entry.value))
    return tuple(values)


__all__ = [
    "HolySiteCatalog",
    "HolySiteDefinition",
    "HolySiteDocument",
    "HolySiteReferenceEdge",
    "HolySiteReport",
    "HolySiteTypeDefinition",
    "HolySiteTypeDocument",
    "ReligionCatalog",
    "ReligionDefinition",
    "ReligionDocument",
    "ReligionOpinion",
    "ReligionReferenceEdge",
    "ReligionReport",
    "ReligiousAspectDefinition",
    "ReligiousAspectDocument",
    "ReligiousAspectOpinion",
    "ReligiousFactionDefinition",
    "ReligiousFactionDocument",
    "ReligiousFigureDefinition",
    "ReligiousFigureDocument",
    "ReligiousFocusDefinition",
    "ReligiousFocusDocument",
    "ReligiousSchoolDefinition",
    "ReligiousSchoolDocument",
    "build_holy_site_catalog",
    "build_holy_site_report",
    "build_religion_catalog",
    "build_religion_report",
    "parse_holy_site_document",
    "parse_holy_site_type_document",
    "parse_religion_document",
    "parse_religious_aspect_document",
    "parse_religious_faction_document",
    "parse_religious_figure_document",
    "parse_religious_focus_document",
    "parse_religious_school_document",
]
